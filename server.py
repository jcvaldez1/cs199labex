import socket
import sys
from _thread import *
import time
from select import select

host = ''
tcp_port = 42000
client_count = 50

s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Sockets Created")

try:
	s_tcp.bind((host,tcp_port))
except socket.error:
	print("Binding failed")
	sys.exit()

print("Socket has been bounded")
s_tcp.listen(20)

def tcp_clientthread(conn):
    data = bytearray()
    #print(data.decode())
    buf = conn.recv(65000)
    #print(buf.decode())
    #while(len(buf)>0):
    #    data = data + buf
    #    buf = conn.recv(65000)
    data = buf.decode()
    print(data)
    reply = "from host " + str(sys.argv[1])
    conn.sendall(reply.encode())
    conn.close()


while True:
    tcp_conn, tcp_addr = s_tcp.accept()
    print("[TCP] Connected with " + tcp_addr[0] + ":" + str(tcp_addr[1]))
    start_new_thread(tcp_clientthread,(tcp_conn,))

s_tcp.close()
