#!/usr/bin/env python2.7
#https://github.com/P1sec/pycrate/wiki/Using-the-pycrate-asn1-runtime

import netfilterqueue
import scapy.all as scapy

from pycrate_asn1dir import S1AP
from pycrate_asn1rt.utils import *
from binascii import hexlify, unhexlify

from pycrate_mobile.NASLTE import *

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())

#    print(scapy_packet.show())

    if scapy_packet.haslayer(scapy.TCP):
        del scapy_packet[scapy.TCP].chksum
        #del scapy_packet[scapy.TCP].len
    elif scapy_packet.haslayer(scapy.UDP):
        del scapy_packet[scapy.UDP].chksum
        del scapy_packet[scapy.UDP].len
    elif scapy_packet.haslayer(scapy.SCTP):
        del scapy_packet[scapy.SCTP].chksum
        del scapy_packet[scapy.SCTP].len
        #scapy_packet[scapy.SCTP][1].data = 'hello world\n\x00'
        try:
            PDU = S1AP.S1AP_PDU_Descriptions.S1AP_PDU
            PDU.from_aper(scapy_packet[scapy.SCTP][1].data)
            print(PDU.to_asn1())
            # Get NAS Layer
            IEs = get_val_at(PDU, ['initiatingMessage', 'value', 'UplinkNASTransport', 'protocolIEs'])
                for ie in IEs:
                    if ie['value'][0]=='NAS-PDU' :
                        Msg, err = parse_NASLTE_MT(ie['value'][1])
                        print(Msg.show())
        except Exception as e:
            print("[Packet Ignore] An exception occurred, ", e)

    del scapy_packet[scapy.IP].len
    del scapy_packet[scapy.IP].chksum

    packet.set_payload(str(scapy_packet))

    #print(packet)
    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()
