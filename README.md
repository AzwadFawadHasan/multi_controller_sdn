# multi_controller_sdn
test mininet multi controller
![multicontrollersdn (1) (1)](https://github.com/user-attachments/assets/a4d07eb9-eb20-484e-a20e-c7583717acb8)

# project structure

```
multi_controller_sdn/
├─ topo/
│  └─ tiny_two_clusters.py
├─ controllers/
│  ├─ child/
│  │  └─ child_app.py
│  └─ master/
│     └─ master_app.py
├─ orchestrator/
│  ├─ orchestrator.py
│  └─ config.yaml
├─ scripts/
│  ├─ run_child_a.sh
│  ├─ run_child_b.sh
│  ├─ run_master.sh
│  └─ run_topo.sh
├─ tests/
│  └─ test_phase1.sh
├─ Makefile
└─ requirements.txt


```
# Run to make scripts executeable
```chmod +x scripts/*.sh```

# Kill old instances
```
sudo mn -c
pkill -f ryu-manager || true
sudo ovs-vsctl del-br s0 s1 s2 2>/dev/null || true
```

# Start in 4 terminals (no sudo except Mininet)

T1 – Child-A (no sudo)

```bash 
make childA
```


T2 – Child-B (no sudo)
```bash 
make childB
```

T3 – Master (no sudo)
```bash 
make master
```

T4 – Topology (Mininet needs sudo)
```bash 
make topo
```
# Ping Drops

if the very first pingall drops a few, run 'pingall' once more (ARP/learning). Because Your later pingall with 0% dropped is correct. The first run dropped because ARP + L2 learning hadn’t populated the tables yet. Once learned, everything’s green.

# Run Validation Tests
Test Health
```
curl -s http://127.0.0.1:8080/health ; echo
```
```
curl -s http://127.0.0.1:8081/health ; echo
```
## Global blocklist (deny hA1 -> hB1 TCP/80 on 10.0.0.0/24)
```
python3 orchestrator/orchestrator.py \
  push-blocklist --rule '{"src_ip":"10.0.0.1","dst_ip":"10.0.0.3","proto":"tcp","dport":80}'
```

## Validate in Mininet (T4)
```
hB1 python3 -m http.server 80 &
hA1 curl -m 2 10.0.0.3:80   # should FAIL (blocked)
hA2 curl -m 2 10.0.0.3:80   # should SUCCEED (not blocked)
```

## Test Failover Master Controller Takeover
Start up another Terminal (T5), to start slave controller monitoring
```
sudo python3 orchestrator/orchestrator.py monitor-failover
```
Then, stop childA (T1 using ctrl+c)
then do pingall (it should still work)
Restart childA
Then rebind back
```
sudo python3 orchestrator/orchestrator.py rebind --to A --switches s1
```
![Visitor Count](https://visitor-badge.laobi.icu/badge?page_id=AzwadFawadHasan.multi_controller_sdn)
