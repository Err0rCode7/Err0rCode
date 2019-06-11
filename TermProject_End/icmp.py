import socket, os
import argparse, struct
import time, sys
import select, random
import functools

#    global    #
TimeOut, TTL = 1 , 0
TTLMax, MyId, data = 30, random.randrange(3000,5000), '' 
ip_length, icmp_length, udp_length, _length = 20, 8, 8, 0
source_ip, dest_ip, protocol = 0, 0, 0
port, beforetime = random.randrange(33500,33600), 0

# Make Checksum
def make_checksum(header) :
    size = len(header)
    if (size % 2) == 1:
        header += b'\x00'
        size += 1
    size = size // 2
    header = struct.unpack('!' + str(size) + 'H', header)
    sum = functools.reduce(lambda x, y :  x+y, header)
    chksum = (sum >> 16) + (sum & 0xffff)
    chksum += chksum >> 16
    chksum = (chksum ^ 0xffff)
    return chksum
# Make IP Packet
def iphdr ():

    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = ip_length+_length+len(data)
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
# Make ICMP Packet #
def icmp_packet ():

    icmp_type = 8 # 8 : request 0 : reply
    icmp_code = 0
    icmp_checksum = 0
    icmp_identifier = MyId
    icmp_sequence= 0
    icmp_pack=struct.pack("!BBHHH",icmp_type,icmp_code,icmp_checksum,icmp_identifier,icmp_sequence)

    icmp_checksum = make_checksum(icmp_pack+data.encode())
    icmp_pack=struct.pack("!BBHHH",icmp_type,icmp_code,icmp_checksum,icmp_identifier,icmp_sequence)

    return icmp_pack
# Make UDP Packet #
def udp_packet() :
    global port
    udp_saddr = socket.inet_aton(source_ip)
    udp_daddr = socket.inet_aton(dest_ip)
    zeroes = 0
    udp_protocol = protocol
    udp_packlen = len(data) + udp_length
    src_port = 8888
    dst_port = port
    Length = udp_packlen
    checksum = 0

    #udp = struct.pack("!4s4sBBHHHHH",udp_saddr,udp_daddr,zeroes,udp_protocol,udp_packlen,src_port,dst_port,Length,checksum)
    #checksum = make_checksum(udp+data.encode())
    udp = struct.pack("!HHHH",src_port,dst_port,Length,checksum)

    return udp

# request ICMP #
def icmp_request (mySocket) :
    global beforetime
    
    packet = iphdr() + icmp_packet() + data.encode()
    beforetime = time.time()
    mySocket.sendto(packet,(dest_ip,0))
# request UDP #
def udp_request (mySocket) :
    global beforetime
    packet = iphdr() + udp_packet() + data.encode()
    beforetime = time.time()

    mySocket.sendto(packet,(dest_ip,port))

# reply icmp #
def receive_icmp (timeout=TimeOut) :

    recSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    
    process = select.select([recSocket],[],[],TimeOut)
    aftertime = time.time()
    # TimeOut #
    if process[0] == [] :      
        return (False, aftertime, None)
  
    recPacket, addr = recSocket.recvfrom(4096*2)
    aftertime = time.time() - beforetime

    ipHeader = recPacket[:20]
    ip_ihl_ver, ip_tos, ip_tot_len, \
    ip_id, ip_frag_off, ip_ttl, ip_proto, \
    ip_checksum, ip_saddr, ip_daddr = struct.unpack(
        "!BBHHHBBHII", ipHeader
    )

    icmpHeader = recPacket[20:28]
    icmp_type,icmp_code,icmp_checksum, \
    icmp_identifier,icmp_sequence = struct.unpack(
        "!BBHHH", icmpHeader
    )
    sourceAdress = socket.inet_ntoa(recPacket[12:16])
    try :
        sourceAdress = socket.gethostbyaddr(sourceAdress)
    except :
        pass    
    # Time Exceed #
    if icmp_type == 11 and icmp_code == 0 :

        ipHeader = recPacket[28:48]
        ip_ihl_ver, ip_tos, ip_tot_len, \
        ip_id, ip_frag_off, ip_ttl, ip_proto, \
        ip_checksum, ip_saddr, ip_daddr = struct.unpack(
            "!BBHHHBBHII", ipHeader
        )

        ihl_ver,tos,tot_len,\
        id,frag_off,ttl,proto,\
        checksum,saddr,daddr = struct.unpack(
            "!BBHHHBBHII", iphdr()
        )
        # protocol, id 등 내가 보낸 것이 맞는 지 확인 #
        if ip_ihl_ver == ihl_ver and (ip_tos == tos or ip_tos == 128) and ip_tot_len == tot_len \
            and ip_id == id and ip_frag_off == frag_off and ip_ttl == 1 \
            and ip_proto == proto and ip_daddr == daddr and \
            (ip_proto == protocol and ip_id == MyId):
            return (False, aftertime, sourceAdress)
    # Destination unreachable #
    elif icmp_type == 3 and icmp_code == 3 :
        
        ipHeader = recPacket[28:48]
        ip_ihl_ver, ip_tos, ip_tot_len, \
        ip_id, ip_frag_off, ip_ttl, ip_proto, \
        ip_checksum, ip_saddr, ip_daddr = struct.unpack(
            "!BBHHHBBHII", ipHeader
        )
        udpHeader = recPacket[48:56]
        recv_src_port,recv_dst_port,recv_Length,recv_checksum = struct.unpack("!HHHH",udpHeader)
        s_port_,d_port,Length,checksum = struct.unpack("!HHHH",udp_packet())
        # protocol, id, port가 내가 보낸 것이 맞는 지 확인 #
        if ip_id == MyId and ip_proto == protocol and recv_dst_port == d_port :
            return (True, aftertime, sourceAdress)

    # Echo Reply #
    elif icmp_type == 0 and icmp_code == 0 :
        
        payload = recPacket[28:].decode()
        # protocol, id , 데이터가 내가 보낸 것이 맞는 지 확인 #
        if payload == data and icmp_identifier == MyId and ip_proto == protocol:
            return (True, aftertime, sourceAdress) 
    # 이외의 패킷 #
    return (False, aftertime, None)

# request and reply #
def Traceroute (mySocket): 
    global TTL, port

    while True :
        if TTLMax == TTL :
            break
        TTL +=1
        port +=1
        reply = False
        sys.stdout.write("%02d " %TTL)
        s1, s2 =0, 0
        for i in range(0,3) :

            if protocol == socket.IPPROTO_ICMP :
                icmp_request(mySocket)
            elif protocol == socket.IPPROTO_UDP :
                udp_request(mySocket)

            reply, time ,sourceAdress = receive_icmp()
            if sourceAdress is not None :
                sys.stdout.write("%0.2f ms " % (time * 1000))

                if type(sourceAdress) == type((0,)) :
                    s1, s2 = sourceAdress[0], sourceAdress[2][0]
                else :
                    s1 = sourceAdress
            elif reply is False :
                sys.stdout.write("   *   ")  

        if s1 is not None and type(s1) == type('str'):
            if type(sourceAdress) == type((0,)) :               
                sys.stdout.write("[%s, %s]" % (s1, s2))   
            else:
                sys.stdout.write("[%s]" % (s1))
                
        sys.stdout.write("\n")
        if reply :    
            break


if __name__ == '__main__' :

    parser = argparse.ArgumentParser(description='args parser')
    parser.add_argument('domain', type=str, metavar='host', help='host')
    parser.add_argument('length', type=int, metavar='size', help='size')
    parser.add_argument('-c', type=int, required=False, metavar='Max_Hops', help='Max_Hops')
    parser.add_argument('-t', type=float, required=False, metavar='recv timeout', help='timeout')
    parser.add_argument('-I', help='ICMP',action='store_true')  
    parser.add_argument('-U', help='UDP',action="store_true")
    parser.add_argument('-p', type=int, required=False, metavar='port', help='port', default=random.randrange(33500,33600))
    args = parser.parse_args()

    source_ip = '0.0.0.0' 
    dest_ip = socket.gethostbyname(args.domain)
    protocol = socket.IPPROTO_ICMP # protocol default
    _length = icmp_length # default

    try:
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

    except socket.error:
        sys.exit()

    if args.U == True :
        protocol = socket.IPPROTO_UDP
        _length = udp_length
        protoname = "UDP"
        if args.p is not None :
            port = args.p

    if args.c is not None :
        TTLMax=args.c
    if args.t is not None :
        TimeOut = args.t

    if args.length-(ip_length + _length) > 64 :
        datalen = 64
    else :
        datalen = args.length-(ip_length + _length)

    data = ''.join(random.choice("abc") for _ in range(datalen))

    print("tracerout to ", args.domain, " (",dest_ip,"), ", TTLMax, " hops max,", args.length,
     "byte packets" )


    Traceroute(mySocket)