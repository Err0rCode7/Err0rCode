## client.py

import socket
import argparse
import os

def run(host, port, file) :
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s :
        s.connect((host, port))
        s.sendall(file.encode())

        data = s.recv(1024)
        
        if not data : # 전송받은 데이터가 없으면 종료합니다.
            print('%s 파일 전송오류' % file)
            return
        
        with open(file, 'ab') as f: 
            try:
                while data: # 전송받을 데이터가 남아있을때 까지 파일을 추가모드로 작성합니다.
                    f.write(data) 
                    data = s.recv(1024)
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

    