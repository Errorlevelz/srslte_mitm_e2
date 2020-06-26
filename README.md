# How to use
```
git clone https://gitlab.com/jed_tw/srslte_mitm  
cd srslte_mitm
```
請自行修改 /etc/srslte/ 底下的設定檔, 目前都為預設 

# 先安裝 docker

# 建立架構
![image](srsLTE_MITM_arch.png)
```
sudo apt install docker-compose -y
sudo docker-compose up
```

# 分別進入 container 裡
#### MEC
```
sudo docker-compose exec mec /bin/bash
```

#### EPC
```
sudo docker-compose exec srsepc /bin/bash
```

#### ENB
```
sudo docker-compose exec srsenb /bin/bash
```

#### UE
```
sudo docker-compose exec srsue /bin/bash
```

# 簡單測試 SCTP 能不能用 (in container)
```
apt install libsctp-dev lksctp-tools -y
```

#### MEC端:
```
python ~/mec_net_cut.py
```

#### EPC端(當 Server)：
```
sctp_darn -H 0 -P 2500 -l
```

#### ENB端(當 Client)：
```
sctp_darn -H 0 -P 2600 -h 10.7.1.2 -p 2500 -s
```

# ZeroMQ Application note
Ref. https://docs.srslte.com/en/latest/app_notes/source/zeromq/source/

#### ENB端
```
srsenb --rf.device_name=zmq --rf.device_args="fail_on_disconnect=true,tx_port=tcp://*:2000,rx_port=tcp://10.8.1.4:2001,id=enb,base_srate=23.04e6"
```
#### UE 端
```
# 可以用 tmux 新增多分頁來測試
srsue --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://10.8.1.2:2000,id=ue,base_srate=23.04e6"
```
```
# 等連線後，在另一個 tmux 分頁
bash ~/ue_net_set.sh
```

# 其他
#### tmux 使用
C-b 指的是 Ctrl + b 同時按  
新增分頁：C-b c  
切換分頁：C-b 數字  
離開tmux：C-b d  
  
#### 移除架構
```
sudo docker-compose down
```

#### Purge (請小心使用, 會 reset docker 所有資料)
`docker system prune`

####  Delete all containers
```
sudo docker rm -f $(docker ps -a -q)
```