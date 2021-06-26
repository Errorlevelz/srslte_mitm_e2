FROM ubuntu:18.04

RUN apt-get update -y && \
apt-get install -y software-properties-common

RUN add-apt-repository ppa:bladerf/bladerf && \
add-apt-repository -y ppa:myriadrf/drivers

RUN apt-get update -y --allow-unauthenticated && \
	apt-get install -y cmake \
	git \
	libzmq3-dev \
	libtool-bin \
	libfftw3-dev \
	libmbedtls-dev \
	libboost-program-options-dev \
	libconfig++-dev \
	libsctp-dev \
	g++ \
	iputils-ping \
	vim \
        tmux \
	libbladerf1 \
	libbladerf2 \
	libbladerf-dev \
	libbladerf-udev \
	autoconf  \
	automake \
	net-tools \
        python-pip \
        libnetfilter-queue-dev \
        iptables

RUN git clone --branch release_20_10_1 https://github.com/srsLTE/srsLTE /root/srsLTE
RUN mkdir /root/srsLTE/build

WORKDIR /root/srsLTE/build
RUN cmake ../ && make -j`nproc` && make install && ldconfig
RUN ./srslte_install_configs.sh service

# netfilterqueue & scapy
RUN pip install netfilterqueue scapy
# pycrate & CryptoMobile
RUN pip install git+https://github.com/P1sec/pycrate git+https://github.com/P1sec/CryptoMobile

# copy files
COPY ./file/epc_tunnel_ue_ip_to_sgi_watch_dog.sh /root/epc_tunnel_ue_ip_to_sgi_watch_dog.sh
COPY ./file/mec_net_pkt_filter.py /root/mec_net_pkt_filter.py
COPY ./file/mec_net_pkt_filter_advanced.py /root/mec_net_pkt_filter_advanced.py
COPY ./file/ue_net_switch_to_cellular.sh /root/ue_net_switch_to_cellular.sh

WORKDIR /root
