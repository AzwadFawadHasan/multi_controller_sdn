# controllers/child/child_app.py
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, DEAD_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet
from ryu.app.wsgi import WSGIApplication, ControllerBase, route
from webob import Response
import json, time



CHILD_INSTANCE_NAME = 'child_api_app'

def _json(obj, status=200):
    return Response(content_type='application/json', body=json.dumps(obj).encode(), status=status)

class ChildApi(ControllerBase):
    def __init__(self, req, link, data, **config):
        super().__init__(req, link, data, **config)
        self.app = data[CHILD_INSTANCE_NAME]

    @route('health', '/health', methods=['GET'])
    def health(self, req, **kwargs):
        return _json({'status': 'ok', 'ts': time.time()})

    @route('stats', '/stats', methods=['GET'])
    def stats(self, req, **kwargs):
        return _json(self.app.stats_snapshot())

    @route('blocklist', '/blocklist', methods=['POST'])
    def blocklist(self, req, **kwargs):
        try:
            payload = json.loads(req.body or b'{}')
            # Minimal validation
            if not isinstance(payload, dict):
                raise ValueError('payload must be JSON object')
            if not (payload.get('src_ip') or payload.get('dst_ip')):
                raise ValueError('need at least src_ip or dst_ip')
            proto = (payload.get('proto') or 'any').lower()
            if 'dport' in payload and proto not in ('tcp','udp'):
                raise ValueError('dport requires proto tcp/udp')

            applied = self.app.install_block_rule(payload)
            return _json({'ok': True, 'applied': payload, 'dpids': applied})
        except Exception as e:
            return _json({'ok': False, 'error': str(e)}, status=400)

class ChildL2Acl(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        wsgi.register(ChildApi, {CHILD_INSTANCE_NAME: self})

        self.mac_to_port = {}     # dpid -> {mac: port}
        self.pkt_counts = {}      # dpid -> packet_in counter
        self.datapaths = {}       # dpid -> datapath

    def stats_snapshot(self):
        return {str(d): {'packet_in': self.pkt_counts.get(d, 0)} for d in self.datapaths.keys()}

    def install_block_rule(self, rule):
        """
        rule: { "src_ip": "...", "dst_ip": "...", "proto": "tcp"|"udp"|"any", "dport": 80|null }
        Installs a high-priority DROP on all datapaths we manage. Returns list of dpids updated.
        """
        updated = []
        for dpid, dp in list(self.datapaths.items()):
            parser = dp.ofproto_parser
            ofp = dp.ofproto
            match_kwargs = {}
            eth_type_ip = {'eth_type': 0x0800}

            if rule.get('src_ip'):
                match_kwargs['ipv4_src'] = rule['src_ip']
            if rule.get('dst_ip'):
                match_kwargs['ipv4_dst'] = rule['dst_ip']

            proto = (rule.get('proto') or 'any').lower()
            l4_match = {}
            if proto in ('tcp', 'udp'):
                match_kwargs['ip_proto'] = 6 if proto == 'tcp' else 17
                if rule.get('dport') is not None:
                    dport = int(rule['dport'])
                    if proto == 'tcp':
                        l4_match['tcp_dst'] = dport
                    else:
                        l4_match['udp_dst'] = dport

            match = parser.OFPMatch(**eth_type_ip, **match_kwargs, **l4_match)
            # Drop = no actions
            mod = parser.OFPFlowMod(datapath=dp, priority=2000, match=match, instructions=[])
            dp.send_msg(mod)
            self.logger.info("[ACL] DROP on dpid=%s rule=%s", dpid, rule)
            updated.append(dpid)
        return updated

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        dp = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            self.datapaths[dp.id] = dp
            self.logger.info("Switch connected dpid=%s", dp.id)
        elif ev.state == DEAD_DISPATCHER:
            if dp.id in self.datapaths:
                self.logger.info("Switch disconnected dpid=%s", dp.id)
                del self.datapaths[dp.id]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features(self, ev):
        dp = ev.msg.datapath
        parser = dp.ofproto_parser
        ofp = dp.ofproto
        # table-miss: punt to controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        dp.send_msg(parser.OFPFlowMod(datapath=dp, priority=0, match=match, instructions=inst))

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in(self, ev):
        msg = ev.msg
        dp = msg.datapath
        parser = dp.ofproto_parser
        ofp = dp.ofproto
        in_port = msg.match['in_port']

        self.pkt_counts[dp.id] = self.pkt_counts.get(dp.id, 0) + 1

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == 0x88cc:  # ignore LLDP
            return

        dpid = dp.id
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][eth.src] = in_port

        out_port = self.mac_to_port[dpid].get(eth.dst, ofp.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofp.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst, eth_src=eth.src)
            inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
            dp.send_msg(parser.OFPFlowMod(datapath=dp, priority=1, match=match, instructions=inst, buffer_id=ofp.OFP_NO_BUFFER))
        else:
            dp.send_msg(parser.OFPPacketOut(datapath=dp, buffer_id=ofp.OFP_NO_BUFFER,
                                            in_port=in_port, actions=actions, data=msg.data))
