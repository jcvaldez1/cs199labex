# SAMPLE RULE SET
default_list = {
        #DATAPATH ID : RULESET 
        1 : [

            {
                "eth_addr_src":   "98:ee:cb:45:b9:08",
                "eth_addr_dst":   "9c:dc:71:f0:c7:c0",
                "eth_addr_fake":  "98:ee:cb:45:b8:9e",
                "ipv4_addr_src":  "10.147.4.68",
                "ipv4_addr_dst":  "64.90.52.128",
                "ipv4_addr_fake": "10.147.4.69",
                "tcp_port_dst":  80,
                "tcp_port_fake": 42000,
            }
        ]
}

if __name__ == "__main__":
    pass
