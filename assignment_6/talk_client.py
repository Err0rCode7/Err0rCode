## client.py

import socket
import argparse
import threading
import time
def run(host, port) :
        clientS= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientS.connect((host, port))


        Sender = threading.Thread(target=SendMsg, args=(clientS,))
        receiver = threading.Thread(target=recvMsg, args=(clientS,host,port))
        Sender.start()
        receiver.start()

        

def SendMsg(s) :
        while True :
                clientMsg = input()
                s.sendall(clientMsg.encode())

def recvMsg(s,h,p) :
        while True :
                Msg = s.recv(1024)
                print("From ",h,":",p,", ", Msg.decode())


if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description="Echo client -p port -i host")
    parser.add_argument('-i', help="host_name", required=True)
    parser.add_argument('-p', help="port_number", required=True)


    args = parser.parse_args()
    run(host=args.i, port=int(args.p))
