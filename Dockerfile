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

RUN git clone --branch release_19_12 https://github.com/srsLTE/srsLTE /root/srsLTE
RUN mkdir /root/srsLTE/build

WORKDIR /root/srsLTE/build
RUN cmake ../ && make -j`nproc` && make install && ldconfig
RUN ./srslte_install_configs.sh service

RUN pip install netfilterqueue scapy

COPY ./file/net_cut.py /root/net_cut.py
WORKDIR /root
