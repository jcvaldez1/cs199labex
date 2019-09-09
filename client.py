import socket
import sys
import time

def main():
    open("./message_back.txt","w").close()
    while 1:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.settimeout(10)
        host = "10.0.0.2"
        port = 42000

        try:
            soc.connect((host, port))
        except:
            print("Connection error")
            #sys.exit()
            continue

        #print("Enter 'quit' to exit")
        #message = input(" -> ")
        message = "bruh"

        soc.sendall(message.encode("utf8"))
        data = soc.recv(65000)
        with open("./message_back.txt","a+") as f:
            f.write(data.decode()+"\n")
            f.close()
        #print(data.decode())
        time.sleep(1)
        soc.close()

if __name__ == "__main__":
    main()
