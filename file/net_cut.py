import netfilterqueue
import scapy.all as scapy

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

    del scapy_packet[scapy.IP].len
    del scapy_packet[scapy.IP].chksum

    packet.set_payload(str(scapy_packet))

    print(packet)
    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()
