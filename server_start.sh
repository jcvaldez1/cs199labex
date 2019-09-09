#!/bin/bash

touch $1_server.pcap;
chmod +rw $1_server.pcap;
sudo tshark -i h$1-eth0 -w $1_server.pcap &
sudo python3 server.py $1
