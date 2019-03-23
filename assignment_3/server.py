## server.py

import socket
import argparse
import os

def run_server(dir, port=4000):
    host = '' ## 127.0.0.1 Loopback
  
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1) ## max 1 client

        conn, addr = s.accept()
        msg = conn.recv(1024)

        fileName = msg.decode()
        fileDir = dir + "\\" + fileName

        
        ItsOk = os.path.exists(fileDir)

        if not ItsOk : # 파일이 존재하지 않으면 -1을 전송하고 종료
            conn.send("-1".encode())
            print("요청받은 파일이 존재하지 않습니다.")
            return
        
        fileSize = os.path.getsize(fileDir) # 파일의 크기를 읽어옵니다.

        print ("요청받은 fileName : %s" % fileDir)
        print ("요청받은 fileSize : %d" % fileSize)

        conn.send(str(fileSize).encode()) # 파일의 크기를 클라이언트에게 전송합니다.

        msg = conn.recv(1024)
        msg = msg.decode()
        if msg != "OK" : # 클라이언트에게 파일이 전송이 잘 이루어지지 않았으면 종료합니다.
            return
        with open(fileDir,'rb') as f : # 이진수로 읽기전용으로 파일을 오픈합니다.
            try:
                data = f.read(fileSize) # 파일의 크기만큼 읽어온 후 클라이언트에게 전송합니다.
                conn.send(data) 
            except Exception as e :
                print(e)

        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Echo server -p port")
    parser.add_argument('-p', help="port_number", required=True)
    parser.add_argument('-d', help="dir_info", required=True)

    args = parser.parse_args()
    run_server(dir=args.d, port=int(args.p))

