import socket, os
import argparse, struct
import time, sys
import select

hopMax = 10
TimeOut = 1
TTL = 0
TTLMax = 30
MyId = 0
def getchecksum(msg) :

    s = 0
    msglen = len(msg)

    for i in range(0, len(msg), 2) :
        w = msg[i] + (msg[i+1] << 8 )
        s = s + w
    if msglen % 2 == 1 : 
        w = msg[len(msg)-1] + 0x00 << 8
        s = s + w 
    s = (s>>16) + (s & 0xffff)
    s = s + (s >> 16)

    s = ~s & 0xffff
    s = socket.htons(s)
    return s

def iphdr ():
    global source_ip, dest_ip,protocol
    global TTL, MyId

    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = 0	
    ip_id = MyId	
    ip_frag_off = 0
    ip_ttl = TTL
    ip_proto = protocol
    ip_checksum = 0	
    ip_saddr = socket.inet_aton ( source_ip )	
    ip_daddr = socket.inet_aton ( dest_ip )

    ip_ihl_ver = (ip_ver << 4) + ip_ihl
    ip_header = struct.pack('!BBHHHBBH4s4s' , ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_checksum, ip_saddr, ip_daddr)

    return ip_header

def icmp_packet ():
    global data
    icmp_type = 8 # 8 : request 0 : reply
    icmp_code = 0
    icmp_checksum = 0
    icmp_identifier = 0
    icmp_sequence= 0
    icmp_pack=struct.pack("!BBHHH",icmp_type,icmp_code,icmp_checksum,icmp_identifier,icmp_sequence)

    icmp_checksum = getchecksum(icmp_pack+data.encode())
    icmp_pack=struct.pack("!BBHHH",icmp_type,icmp_code,icmp_checksum,icmp_identifier,icmp_sequence)

    return icmp_pack

def icmp_request (mySocket) :
    global source_ip, dest_ip
    global TTL
    packet = iphdr() + icmp_packet() + data.encode()
    mySocket.sendto(packet,(dest_ip,0))
    TTL +=1
    print("icmp request success TTL : ",TTL)
    

def receive_icmp (mySocket,timeout=TimeOut) :
    global MyId
    global dest_ip, source_ip

    recSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    #startTime = time.time()
    process = select.select([recSocket],[],[],timeout)

    if process[0] == [] :
        print("icmp reply timeout")
        return 
  
    recPacket, addr = recSocket.recvfrom(4096)
    print("icmp reply success")
	
    ipHeader = recPacket[:20]
    ip_ihl_ver, ip_tos, ip_tot_len, \
    ip_id, ip_frag_off, ip_ttl, ip_proto, \
    ip_checksum, ip_saddr, ip_daddr = struct.unpack(
        "!BBHHHBBHII", ipHeader
    )
    print("source_ip :",hex(ip_saddr), " dest_ip:",hex(ip_daddr))
    icmpHeader = recPacket[20:28]
    icmp_type,icmp_code,icmp_checksum, \
    icmp_identifier,icmp_sequence = struct.unpack(
        "!BBHHH", icmpHeader
    )

    if icmp_identifier == MyId :
        return ip_saddr

def Traceroute (mySocket):
    global TTL, TTLMax
    while True :
        icmp_request(mySocket)
        ip_saddr=receive_icmp(mySocket)
        if(  TTL == TTLMax ) :    
            break
        

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='This is a simpe packet sniffer')
    parser.add_argument('-d', type=str, required=True, metavar='domain', help='domain')
    parser.add_argument('-t', type=str, required=False, metavar='timeout', help='timeout')
    #parser.add_argument('-l', type=str, required=True, metavar='domain', help='domain')  
    #parser.add_argument('-h', type=str, required=True, metavar='domain', help='domain')

    args = parser.parse_args()

    source_ip = '192.168.93.131' #socket.gethostbyname(socket.getfqdn()) #
    dest_ip = socket.gethostbyname(args.d)
    protocol = socket.IPPROTO_ICMP # ICMP TCP UDP ( input )
    data = 'hihihi'

    try:
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

    except socket.error:
        sys.exit()

    Traceroute(mySocket)