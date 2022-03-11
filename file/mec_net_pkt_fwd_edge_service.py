#!/usr/bin/env python2.7
#https://github.com/P1sec/pycrate/wiki/Using-the-pycrate-asn1-runtime
import netfilterqueue
import scapy.all as scapy
from scapy.all import Ether, send, IP, sr, sr1, srp
import re
import os
from pycrate_asn1dir import S1AP
from pycrate_asn1rt.utils import *
from binascii import hexlify, unhexlify
from scapy.layers.inet import IP, UDP
from pycrate_mobile.NASLTE import *
from scapy.config import conf
from pycrate_mobile.NAS import *
from scapy.contrib.gtp import *
import socket

dns_hosts = {
    b"www.google.com.": "10.5.1.2",
    b"google.com.": "10.5.1.2",
    b"facebook.com.": "10.5.1.2"
}

service_ip = {
   '10.5.1.2'
}

INNER_IP_BACK_TEID = 0x0

def process_packet(packet):
    global INNER_IP_BACK_TEID

    scapy_packet = scapy.IP(packet.get_payload())

    #print(scapy_packet.show())

    if scapy_packet.haslayer(scapy.DNSRR):
        print("[Before]:", scapy_packet.summary())
        try:
            scapy_packet = modify_packet(scapy_packet)
        except IndexError:
            pass
        print("[After ]:", scapy_packet.summary())

    if scapy_packet.haslayer(GTP_U_Header):
        try:
            INNER_IP_src = scapy_packet[scapy.UDP][GTP_U_Header][scapy.IP].src
            INNER_IP_dst = scapy_packet[scapy.UDP][GTP_U_Header][scapy.IP].dst
            INNER_IP_TOS = scapy_packet[scapy.UDP][GTP_U_Header][scapy.IP].tos
            INNER_IP_TEID = scapy_packet[scapy.UDP][GTP_U_Header].teid
            if scapy_packet[scapy.UDP][GTP_U_Header][scapy.IP].haslayer(scapy.ICMP):
                print ("[+] INNER_IP_src ", INNER_IP_src)
                print ("[+] INNER_IP_dst ", INNER_IP_dst)
                print ("[+] INNER_IP_TEID ", INNER_IP_TEID)
                print ("[+] INNER_IP_BACK_TEID ", INNER_IP_BACK_TEID)

                if INNER_IP_dst in service_ip:
                    scapy_packet2 = scapy_packet['GTP_U_Header']['IP']
                    scapy_packet2.src = '10.5.2.3'
                    del scapy_packet2[scapy.ICMP].chksum
                    #del scapy_packet2[scapy.ICMP].len
                    del scapy_packet2.len
                    del scapy_packet2.chksum

                    print("[+] scapy_packet hope send back ", scapy_packet2.src)
                    send(scapy_packet2, iface='eth2', inter=0)

            elif scapy_packet[scapy.UDP][GTP_U_Header][scapy.IP].haslayer(scapy.TCP):
                tcpSport = scapy_packet[scapy.UDP][GTP_U_Header][scapy.IP][scapy.TCP].sport
                tcpDport = scapy_packet[scapy.UDP][GTP_U_Header][scapy.IP][scapy.TCP].dport

                print ("[+] tcpSport ", tcpSport)
                print ("[+] tcpDport ", tcpDport)
                print ("[+] INNER_IP_src ", INNER_IP_src)
                print ("[+] INNER_IP_dst ", INNER_IP_dst)
                print ("[+] INNER_IP_TEID ", INNER_IP_TEID)
                print ("[+] INNER_IP_BACK_TEID ", INNER_IP_BACK_TEID)
                
                if INNER_IP_dst in service_ip:
                    scapy_packet2 = scapy_packet['GTP_U_Header']['IP']
                    scapy_packet2.src = '10.5.2.3'
                    del scapy_packet2[scapy.TCP].chksum
                    #del scapy_packet2[scapy.TCP].len
                    del scapy_packet2.len
                    del scapy_packet2.chksum

                    print("[+] scapy_packet hope send back ", scapy_packet2.src)
                    send(scapy_packet2, iface='eth2')

            elif scapy_packet[scapy.UDP][GTP_U_Header][scapy.IP].haslayer(scapy.UDP):
                udpBSport = scapy_packet[scapy.UDP][GTP_U_Header][scapy.IP][scapy.UDP].sport
                if udpBSport==53:
                    INNER_IP_BACK_TEID = scapy_packet[scapy.UDP][GTP_U_Header].teid
                    print ("53>>>>>>INNER_IP_BACK_TEID ", INNER_IP_BACK_TEID)

        except Exception as e:
            #pass
            print("[Packet Ignore GTP] An exception occurred, ", e)

    elif scapy_packet.haslayer(scapy.TCP):
        #print(scapy_packet.show())
        service_packet = IP(dst="10.6.1.2", src="10.7.1.2")/UDP(sport=2152, dport=2152) / GTP_U_Header(teid=INNER_IP_BACK_TEID) / scapy_packet
        service_packet[scapy.UDP][GTP_U_Header][scapy.IP].dst = "172.16.0.2"
        del service_packet[scapy.IP].len
        del service_packet[scapy.IP].chksum
        del service_packet[scapy.UDP].len
        del service_packet[scapy.UDP].chksum
        del service_packet[scapy.UDP][GTP_U_Header][scapy.IP].len
        del service_packet[scapy.UDP][GTP_U_Header][scapy.IP].chksum
        #del packet[scapy.UDP][GTP_U_Header][scapy.IP][scapy.TCP].len
        del service_packet[scapy.UDP][GTP_U_Header][scapy.IP][scapy.TCP].chksum

        #print(service_packet.show())
        send(service_packet, iface="eth1")
        print ("[+] Respond Sent!")
        #del scapy_packet[scapy.TCP].len

    elif scapy_packet.haslayer(scapy.ICMP):
        #print(scapy_packet.show())
        service_packet = IP(dst="10.6.1.2", src="10.7.1.2")/UDP(sport=2152, dport=2152) / GTP_U_Header(teid=INNER_IP_BACK_TEID) / scapy_packet
        service_packet[scapy.UDP][GTP_U_Header][scapy.IP].dst = "172.16.0.2"
        del service_packet[scapy.IP].len
        del service_packet[scapy.IP].chksum
        del service_packet[scapy.UDP].len
        del service_packet[scapy.UDP].chksum
        del service_packet[scapy.UDP][GTP_U_Header][scapy.IP].len
        del service_packet[scapy.UDP][GTP_U_Header][scapy.IP].chksum
        del service_packet[scapy.UDP][GTP_U_Header][scapy.IP][scapy.ICMP].chksum

        #print(service_packet.show())
        send(service_packet, iface="eth1", inter=0)
        print ("[+] Respond Sent!")

    elif scapy_packet.haslayer(scapy.UDP):
        del scapy_packet[scapy.UDP].chksum
        del scapy_packet[scapy.UDP].len

    elif scapy_packet.haslayer(scapy.SCTP):
        del scapy_packet[scapy.SCTP].chksum
        del scapy_packet[scapy.SCTP].len

        try:
            PDU = S1AP.S1AP_PDU_Descriptions.S1AP_PDU      
            PDU.from_aper(scapy_packet[scapy.SCTP][1].data)
            IEs = get_val_at(PDU, ['initiatingMessage', 'value', 'InitialContextSetupRequest', 'protocolIEs', 3 ,'value', 'E-RABToBeSetupListCtxtSUReq' ])
            
            for ie in IEs:
                Msg_GTP = ie['value'][1]['gTP-TEID']
                Msg, err = parse_NAS_MO(ie['value'][1]['nAS-PDU'])
                Msg1, err1 = parse_NAS_MO(Msg['NASMessage'].get_val())
                s = hexlify(Msg1['ESMContainer']['ESMActDefaultEPSBearerCtxtRequest']['PDNAddr']['PDNAddr']['Addr'].get_val())
                d = hexlify(Msg1['ESMContainer']['ESMActDefaultEPSBearerCtxtRequest']['ProtConfig']['ProtConfig']['Config'][0]['Cont'].get_val())
                INNER_ATTACH_IP = '.'.join(str(int(i, 16)) for i in [s[i:i+2] for i in range(0, len(s), 2)])
                print (INNER_ATTACH_IP)
                print ('.'.join(str(int(i, 16)) for i in [d[i:i+2] for i in range(0, len(d), 2)]))
                
        except Exception as e:
            pass
            #print("[Packet Ignore] An exception occurred, ", e)

        try:
            PDU = S1AP.S1AP_PDU_Descriptions.S1AP_PDU      
            PDU.from_aper(scapy_packet[scapy.SCTP][1].data)
            IG = get_val_at(PDU, ['successfulOutcome', 'value', 'InitialContextSetupResponse', 'protocolIEs', 2, 'value', 'E-RABSetupListCtxtSURes', 0, 'value', 'E-RABSetupItemCtxtSURes', 'gTP-TEID'])
            #print ("1>>>>>>", hexlify(IG))
            print ("UE's GTP-TUNNEL ID is " + hexlify(IG))
        except Exception as e:
            pass
        #    #print("[Packet Ignore] An exception occurred, ", e)


    del scapy_packet[scapy.IP].len
    del scapy_packet[scapy.IP].chksum

    packet.set_payload(str(scapy_packet))


    #print(packet)
    packet.accept()

def modify_packet(packet):
    """
    Modifies the DNS Resource Record `packet` ( the answer part)
    to map our globally defined `dns_hosts` dictionary.
    For instance, whenever we see a google.com answer, this function replaces
    the real IP address (172.217.19.142) with fake IP address (192.168.1.100)
    """
    # get the DNS question name, the domain name
    qname = packet[scapy.DNSQR].qname
    if qname not in dns_hosts:
        # if the website isn't in our record
        # we don't wanna modify that
        print("no modification:", qname)
        return packet
    # craft new answer, overriding the original
    # setting the rdata for the IP we want to redirect (spoofed)
    # for instance, google.com will be mapped to "192.168.1.100"
    packet[scapy.DNS].an = scapy.DNSRR(rrname=qname, rdata=dns_hosts[qname])
    # set the answer count to 1
    packet[scapy.DNS].ancount = 1
    # delete checksums and length of packet, because we have modified the packet
    # new calculations are required ( scapy will do automatically )
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.UDP].len
    del packet[scapy.UDP].chksum
    del packet[scapy.UDP][GTP_U_Header][scapy.IP].len
    del packet[scapy.UDP][GTP_U_Header][scapy.IP].chksum
    del packet[scapy.UDP][GTP_U_Header][scapy.IP][scapy.UDP].len
    del packet[scapy.UDP][GTP_U_Header][scapy.IP][scapy.UDP].chksum
    # return the modified packet
    #packet.show()
    return packet

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()

