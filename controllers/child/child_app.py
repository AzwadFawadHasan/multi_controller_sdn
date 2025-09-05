# controllers/child/child_app.py
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp
from ryu.app.wsgi import WSGIApplication, ControllerBase, route
from webob import Response
import json
import time

CHILD_INSTANCE_NAME = 'child_api_app'

def _json(obj, status=200):
    body = json.dumps(obj).encode('utf-8')
    return Response(content_type='application/json', body=body, status=status)

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
            payload = json.loads(req.body)
            self.app.install_block_rule(payload)
            return _json({'ok': True, 'applied': payload})
        except Exception as e:
            return _json({'ok': False, 'error': str(e)}, status=400)

class ChildL2Acl(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        wsgi.register(ChildApi, {CHILD_INSTANCE_NAME: self})
        self.mac_to_port = {}     # dpid -> {mac:port}
        self.dpids = set()
        self.pkt_counts = {}      # dpid -> count

    def stats_snapshot(self):
        return {str(d): {'packet_in': self.pkt_counts.get(d, 0)} for d in self.dpids}

    def install_block_rule(self, rule):
        """
        rule: { "src_ip": "10.0.1.1", "dst_ip": "10.0.2.1",
                "proto": "tcp"|"udp"|"any", "dport": 80|null }
        Install a DROP on all datapaths we manage.
        """
        for dpid in list(self.dpids):
            dp = self._get_dp_by_id(dpid)
            if not dp: 
                continue
            ofp = dp.ofproto
            parser = dp.ofproto_parser
            match_fields = {}

            if rule.get('src_ip'):
                match_fields['ipv4_src'] = rule['src_ip']
            if rule.get('dst_ip'):
                match_fields['ipv4_dst'] = rule['dst_ip']

            proto = rule.get('proto', 'any').lower()
            if proto in ('tcp', 'udp'):
                match_fields['ip_proto'] = 6 if proto == 'tcp' else 17

            if rule.get('dport') and proto in ('tcp','udp'):
                # Layer-4 destination port match
                if proto == 'tcp':
                    match = parser.OFPMatch(eth_type=0x0800, **match_fields, tcp_dst=int(rule['dport']))
                else:
                    match = parser.OFPMatch(eth_type=0x0800, **match_fields, udp_dst=int(rule['dport']))
            else:
                match = parser.OFPMatch(eth_type=0x0800, **match_fields)

            # Drop = instruction with no actions (or send to controller with no-output)
            inst = []
            mod = parser.OFPFlowMod(datapath=dp, priority=2000, match=match, instructions=inst)
            dp.send_msg(mod)
            self.logger.info("[ACL] DROP installed on dpid=%s rule=%s", dpid, rule)

    def _get_dp_by_id(self, dpid):
        # Controller keeps datapaths in app_manager; we track ids
        for dp in list(self.registry.datapaths.values()):
            if dp.id == dpid:
                return dp
        return None

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features(self, ev):
        dp = ev.msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        self.dpids.add(dp.id)
        self.logger.info("Switch connected dpid=%s", dp.id)

        # Table-miss → send to controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        dp.send_msg(parser.OFPFlowMod(datapath=dp, priority=0, match=match, instructions=inst))

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        in_port = msg.match['in_port']

        self.pkt_counts[dp.id] = self.pkt_counts.get(dp.id, 0) + 1

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == 0x88cc:  # ignore LLDP
            return

        dpid = dp.id
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][eth.src] = in_port

        # L2 learning switching
        out_port = self.mac_to_port[dpid].get(eth.dst, ofp.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofp.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst, eth_src=eth.src)
            inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
            dp.send_msg(parser.OFPFlowMod(datapath=dp, priority=1, match=match, instructions=inst, buffer_id=ofp.OFP_NO_BUFFER))
        else:
            dp.send_msg(parser.OFPPacketOut(datapath=dp, buffer_id=ofp.OFP_NO_BUFFER,
                                            in_port=in_port, actions=actions, data=msg.data))
