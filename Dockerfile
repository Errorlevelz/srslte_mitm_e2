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

#add own dir, loacl dir name: srsran_oenb
#ADD srsran_oenb /root/srsRAN
RUN git clone --branch release_21_10 https://github.com/srsran/srsRAN /root/srsRAN
RUN mkdir /root/srsRAN/build

WORKDIR /root/srsRAN/build
RUN cmake ../ && make -j`nproc` && make install && ldconfig
RUN ./srsran_install_configs.sh service

# netfilterqueue & scapy
RUN pip install netfilterqueue scapy
# pycrate & CryptoMobile
RUN pip install git+https://github.com/P1sec/pycrate git+https://github.com/P1sec/CryptoMobile

WORKDIR /root
