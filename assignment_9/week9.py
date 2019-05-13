import socket
import os
import argparse
import struct
import time

ETH_P_ALL = 0x0003
ETH_SIZE = 14
HeaderLength = 0

def dumpcode(buf):
    print("Raw Data")
    print("%7s"% "offset ", end='')

    for i in range(0, 16):
        print("%02x " % i, end='')

        if not (i%16-7):
            print("- ", end='')

    print("")

    for i in range(0, len(buf)):
        if not i%16:
            print("0x%04x" % i, end= ' ')

        print("%02x" % buf[i], end= ' ')

        if not (i % 16 - 7):
            print("- ", end='')

        if not (i % 16 - 15):
            print(" ")

    print("")

def make_ethernet_header (raw_data) :
    global Ether_Type
    ether = struct.unpack('!6B6BH', raw_data)
    if ether[12]==2048 :
        Ether_Type = 1
    else :
        Ether_Type = 0
    return {'dst':'%02x:%02x:%02x:%02x:%02x:%02x' % ether[:6],
        'src':'%02x:%02x:%02x:%02x:%02x:%02x' % ether[6:12],
        'ether_type':ether[12]}

def check_ip (raw_data) :
    global HeaderLength
    global Ether_Type
    mask=0x0F
    check = raw_data
    HeaderLength = ((check & mask) *4) + ETH_SIZE

def make_ip_header (raw_data) :
    global Ether_Type
    if Ether_Type == 0 :
        pass
    mask=0x0F
    ip = struct.unpack('!BBHHHBBH4B4B', raw_data)
    return {'[version]':'%x' %(ip[0]>>4),
        '[Header Length]':'%x' %(ip[0] & mask),
        '[Type of Service]':ip[1],
        '[Total Packet Length]':ip[2],
        '[id]':ip[3],
        '[flag]':'%x' %(ip[4]>>13),
        '[offset]':'%x' %(ip[4]& (0x1FFF)),
        '[ttl]':ip[5],
        '[protocil]':ip[6],
        '[checksum]':ip[7],
        '[src]': '%d.%d.%d.%d' %ip[8:12],
        '[dst]': '%d.%d.%d.%d' %ip[12:16]
    }

def sniffing(nic):
    global HeaderLength
    if os.name == 'nt':
        address_familiy = socket.AF_INET
        protocol_type = socket.IPPROTO_IP
    else:
        address_familiy = socket.AF_PACKET
        protocol_type = socket.ntohs(ETH_P_ALL)

    with socket.socket(address_familiy, socket.SOCK_RAW, protocol_type) as sniffe_sock:
        sniffe_sock.bind((nic, 0))

        while True :

            if os.name == 'nt':
                sniffe_sock.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
                sniffe_sock.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)

            data, _ = sniffe_sock.recvfrom(65535)
            ethernet_header = make_ethernet_header(data[:ETH_SIZE])
            check_ip(data[ETH_SIZE])
            ip_header = make_ip_header(data[ETH_SIZE:HeaderLength])
            print("Ethernet Header")
            for item in ethernet_header.items() :
                print('{0} : {1}'.format(item[0], item[1]))
            print()
            print("IP HEADER")
            for item in ip_header.items() :
                print('{0} : {1}'.format(item[0], item[1]))

            if os.name == 'nt':
                sniffe_sock.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)

            dumpcode(data)
            time.sleep(3)
            print('\n\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is a simpe packet sniffer')
    parser.add_argument('-i', type=str, required=True, metavar='NIC name', help='NIC name')
    args = parser.parse_args()

    sniffing(args.i)