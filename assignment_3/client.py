## client.py

import socket
import argparse
import os

def run(host, port, file) :
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s :
        s.connect((host, port))
        s.sendall(file.encode())

        data = s.recv(1024)
        data = data.decode()
        if data == "-1" : # 요청한 파일이 없으면 종료합니다.
            print("요청한 파일이 존재하지 않습니다.")
            return
        FileSize = int(data)
        msg = "OK"
        s.sendall(msg.encode()) # 서버에게 OK 사인을 전송합니다.
        
        data = s.recv(FileSize) # 파일의 크기만큼 전송을 받습니다.

        with open(file, 'ab') as f: 
            try:
                f.write(data) # 파일을 만듭니다.
            except Exception as e:
                print(e)
        
        print ("요청해서 받은 fileName : %s " % file)
        print ("요청해서 받은 fileSize : %d" % os.path.getsize(file))
        


if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description="Echo client -p port -i host")
    parser.add_argument('-p', help="port_number", required=True)
    parser.add_argument('-i', help="host_name", required=True)
    parser.add_argument('-f', help="file_name", required=True)
    
    args = parser.parse_args()
    run(host=args.i, port=int(args.p), file=args.f)

    