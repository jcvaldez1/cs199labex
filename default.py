# SAMPLE RULE SET
default_list = {
        #DATAPATH ID : RULESET 
        1 : [

            {
                "eth_addr_src":   "00:00:00:00:00:01",
                "eth_addr_dst":   "00:00:00:00:00:02",
                "eth_addr_fake":  "00:00:00:00:00:03",
                "ipv4_addr_src":  "10.0.0.1",
                "ipv4_addr_dst":  "10.0.0.2",
                "ipv4_addr_fake": "10.0.0.3",
                "tcp_port_dst":   42000,
                "tcp_port_fake":  42069
            },
        ],

        2 : [

            {
                "eth_addr_src":   "00:00:00:00:00:01",
                "eth_addr_dst":   "00:00:00:00:00:03",
                "eth_addr_fake":  "00:00:00:00:00:04",
                "ipv4_addr_src":  "10.0.0.1",
                "ipv4_addr_dst":  "10.0.0.3",
                "ipv4_addr_fake": "10.0.0.4",
                "tcp_port_dst":   42069,
                "tcp_port_fake":  6942
            },
        ]
}

if __name__ == "__main__":
    pass
