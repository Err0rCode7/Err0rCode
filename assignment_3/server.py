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
        fileSize = os.path.getsize(fileDir) # 파일의 크기를 가져옵니다.
        
        if not os.path.exists(fileDir) : # 파일이 존재하지 않으면 종료
            return
        

        print ("요청받은 fileName : %s" % fileDir)
        print ("요청받은 fileSize : %d" % fileSize)
        with open(fileDir,'rb') as f : # 이진수로 읽기전용으로 파일을 오픈합니다.
            try:
                data = f.read()
                while data: # 파일 내용이 없을때까지 다 보냅니다.
                    conn.send(data) 
                    data = f.read() 
            except Exception as e :
                print(e)

        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Echo server -p port")
    parser.add_argument('-p', help="port_number", required=True)
    parser.add_argument('-d', help="dir_info", required=True)

    args = parser.parse_args()
    run_server(dir=args.d, port=int(args.p))

