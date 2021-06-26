#!/bin/bash

PROGNAME=$(basename $0)
VERSION="2021.06.26-2330"

usage () {
    echo "Usage: bash ./${PROGNAME} <IMSI> <SGi Interface Name> [if_masq]"
    echo -e "\tExample: bash ./${PROGNAME} 001010123456789 eth2"
    echo -e "[!] If use 'if_masq' parameter, the UE's network traffic will be forwarding to the outside."
    echo -e "\tExample: bash ./${PROGNAME} 001010123456789 eth2 if_masq"
}

if [ "$1/" == "/" ]; then usage; exit; fi
if [ "$2/" == "/" ]; then usage; exit; fi
if [ "$3/" != "/" ] && [ "$3/" != "if_masq/" ]; then usage; exit; fi

WATCH_IMSI=$1
SGI_IF=$2
DO_IF_MASQ=`if [ "$3/" == "if_masq/" ]; then echo true; else echo false; fi`

echo "[INFO][`date '+%Y/%m/%d %H:%M:%S'`] Start to Watch with IMSI $WATCH_IMSI"
if ${DO_IF_MASQ} ; then echo "[INFO][`date '+%Y/%m/%d %H:%M:%S'`] 'if_masq' parameter is setting" ; fi

while [ true ]
do
    CURRENT_IP=`cat /tmp/epc_console.log | grep "SPGW Allocated IP" | grep $WATCH_IMSI | tail -1 | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b"`
    SrsLTE_IP_Record=`cat /tmp/${WATCH_IMSI}.srsLTE_IP_Record | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b"`
    if [ "$CURRENT_IP" != "$SrsLTE_IP_Record" ]; then
        echo "[INFO][`date '+%Y/%m/%d %H:%M:%S'`] SPGW Allocated new IP $CURRENT_IP to IMSI $WATCH_IMSI"
        echo "[INFO][`date '+%Y/%m/%d %H:%M:%S'`] Update the mapping .."
        iptables -F -t nat
        if ${DO_IF_MASQ} ; then
            iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE
            echo "[INFO][`date '+%Y/%m/%d %H:%M:%S'`] UE($WATCH_IMSI)'s network traffic will be forwarding to the outside."
        fi
        iptables -A PREROUTING -t nat -i $SGI_IF -p tcp -j DNAT --to-destination $CURRENT_IP
        echo $CURRENT_IP > /tmp/${WATCH_IMSI}.srsLTE_IP_Record
        echo "[INFO][`date '+%Y/%m/%d %H:%M:%S'`] Done! Watch Next Action .."
    fi
    sleep 2s
done
