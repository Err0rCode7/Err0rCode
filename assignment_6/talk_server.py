## server.py

import socket
import argparse
import threading
import time
def run_server(port=4000):
        host = '' ## 127.0.0.1 Loopback

        serverS = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        serverS.bind((host, port))
        serverS.listen(1) ## max 1 client

        conn, addr = serverS.accept()
        print("Connected to : ",addr[0],":",addr[1])
        Sender = threading.Thread(target=SendMsg, args=(conn,))
        receiver = threading.Thread(target=recvMsg, args=(conn, addr))
        Sender.start()
        receiver.start()

        
def SendMsg(conn):
        while True :
                serverMsg = input()
                conn.sendall(serverMsg.encode())   ## To send string , we need to encode it

def recvMsg(conn,addr):
        while True :
                Msg = conn.recv(1024)
                print("From ",addr[0],":",addr[1],", ", Msg.decode())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Echo server -p port")
    parser.add_argument('-p', help="port_number", required=True)

    args = parser.parse_args()   
    run_server(port=int(args.p))

