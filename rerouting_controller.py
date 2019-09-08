# Copyright (C) 2016 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# BASE RYU PACKAGE REQS
from operator import attrgetter 
#from ryu.app import meter_poller
#import meter_poller
import learning_switch
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

# IMPORT SOME CONSTANTS
from ryu.lib.packet.ether_types import *
from ryu.lib.packet.in_proto import *

# CUSTOM CONFIG
#from ryu.cfg import CONF

class Rerouter(learning_switch.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(Rerouter, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.aliaser_thread = hub.spawn(self._aliaser_boi)
        self.mon = hub.spawn(self._monitor)


    def _aliaser_boi(self):

        while True:
            '''
                NOTE: THE DEFAULT CONFIG FILE IS PLACED HERE
                      WHICH ENABLES EDITING DURING RUN TIME
            '''
            from default import *

            for dp_id, rules in default_list.iteritems():
                for rule_set in  rules:
                    if not dp_id in self.datapaths:
                        continue
                    print("\nPUTANGINAMO\n")
                    dp = self.datapaths[dp_id]
                    ofproto = dp.ofproto
                    parser = dp.ofproto_parser
                    act_set = parser.OFPActionSetField
                    act_out = parser.OFPActionOutput

                    ''' 
                        NOTE: The eth_type and ip_proto fields 
                              have constants imported from 
                              ether_types and in_proto.
                    '''

                    # OUTGOING PACKET FLOWS (SRC PERCEPTION)
                    match = parser.OFPMatch( eth_type=ETH_TYPE_IP,
                                             ip_proto=IPPROTO_IP,
                                             ipv4_src=rule_set["ipv4_addr_src"],
                                             ipv4_dst=rule_set["ipv4_addr_dst"],
                                            )

                    actions = [ act_set(eth_dst  = rule_set["eth_addr_fake"]      ),
                                act_set(ipv4_dst = rule_set["ipv4_addr_fake"]     ),
                                act_set(tcp_dst  = rule_set["tcp_port_fake"]      ),
                                act_out(self.mac_to_port[dp_id][ rule_set["eth_addr_fake"] ] ) 
                                ]

                    # The second param passed to add_flow
                    # is an arbitrary value (for now)
                    super(Rerouter, self).add_flow(dp, 15, match, actions)

                    # INGOING PACKET FLOWS (SRC PERCEPTION)
                    match = parser.OFPMatch( eth_type=ETH_TYPE_IP,
                                             ip_proto=IPPROTO_IP,
                                             ipv4_src=rule_set["ipv4_addr_fake"],
                                             ipv4_dst=rule_set["ipv4_addr_src"],
                                             )

                    actions = [ act_set(eth_src  = rule_set["eth_addr_dst"]      ),
                                act_set(ipv4_src = rule_set["ipv4_addr_dst"]     ),
                                act_set(tcp_src  = rule_set["tcp_port_dst"]      ),
                                act_out(self.mac_to_port[dp_id][ rule_set["eth_addr_src"] ] ) 
                                ]

                    # The second param passed to add_flow 
                    # is an arbitrary value (for now)
                    super(Rerouter, self).add_flow(dp, 15, match, actions)
            # hub sleep value is also arbitrary
            hub.sleep(10)


    # CLEANER FOR DEAD DATAPATHS
    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            self.logger.info('%016x %8x %17s %8x %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)
