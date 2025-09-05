# Standalone Ryu master app: L2 learning + ACL (drop rules) with no WSGI.
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet

class MasterL2Acl(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mac_to_port = {}   # dpid -> {mac:port}
        self.dpids = set()

    # --- Optional helper if you later want to push drops via ryu-manager CLI vars or config ---
    # Example usage (when starting):  ryu-manager --observe-links controllers/master/master_app.py
    # and then call a method via Ryu RPC. For now we omit RPC and REST to keep it simple.

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features(self, ev):
        dp = ev.msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        self.dpids.add(dp.id)
        self.logger.info("[MASTER] Switch connected dpid=%s", dp.id)

        # table-miss: send to controller
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

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == 0x88cc:  # ignore LLDP
            return

        dpid = dp.id
        self.mac_to_port.setdefault(dpid, {})
        # learn source MAC
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

    # Simple API to install a drop rule programmatically (not exposed via REST here).
    def install_drop(self, dp, match):
        parser = dp.ofproto_parser
        mod = parser.OFPFlowMod(datapath=dp, priority=2000, match=match, instructions=[])
        dp.send_msg(mod)
        self.logger.info("[MASTER] DROP installed on dpid=%s match=%s", dp.id, match)
