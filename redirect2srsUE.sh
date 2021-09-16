#!/bin/sh
sudo iptables -F -t nat

# Let Contianer connect to the Internet
sudo iptables -t nat -A POSTROUTING -s 10.9.1.0/24 -j MASQUERADE

# In -> Out (ip)
sudo iptables -t nat -A POSTROUTING --dst 10.9.2.2 -j MASQUERADE
# In -> Out (all)
#sudo iptables -t nat -A POSTROUTING -o eno1 -j MASQUERADE
# Out -> In
sudo iptables -A PREROUTING -t nat -i wlp58s0 -j DNAT --to 10.9.2.2

# FORWARD ALL Port
sudo iptables --policy FORWARD ACCEPT
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward 1>/dev/null
