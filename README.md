# How to use
`git clone https://gitlab.com/jed_tw/srslte_mitm`
`cd srslte_mitm`

# 先安裝 docker

# 建立架構
`sudo apt install docker-compose`
`sudo docker-compose up`

# 分別進入 container 裡
## MEC
`sudo docker-compose exec mec /bin/bash`

## EPC
`sudo docker-compose exec srsepc /bin/bash`

## ENB
`sudo docker-compose exec srsenb /bin/bash`


## 簡單測試 SCTP 能不能用 (in container)
`apt-get install libsctp-dev lksctp-tools

### MEC端:
`python ~/net_cut.py`

### EPC端(當 Server)：
`sctp_darn -H 0 -P 2500 -l`

### ENB端(當 Client)：
`sctp_darn -H 0 -P 2600 -h 10.6.1.2 -p 2500 -s`

## 其他
# 移除架構
`sudo docker-compose down`

# Purge (請小心使用, 會 reset docker 所有資料)
`docker system prune`

#  Delete all containers
`sudo docker rm -f $(docker ps -a -q)`