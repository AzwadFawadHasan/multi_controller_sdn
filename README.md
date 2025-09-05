# multi_controller_sdn
test mininet multi controller

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


# PHASE 2:
## Clean restart first (optional but recommended):
```bash
sudo mn -c
```
```bash
pkill -f ryu-manager || true
```
```bash
sudo ovs-vsctl del-br s0 s1 s2 s0a s0b s1a s2a s1b s2b 2>/dev/null || true
```

## Open up 5 terminals:
T1
```bash 
make childA
```
T2
```bash
make childB
```
T3
```bash
make master
```
T4
```bash
make two_sites
# If first ping drops a few, run 'pingall' again (learning/ARP)
```
T5
```bash
# Health across both sites
python3 orchestrator/orchestrator.py health

# Global blocklist across both domains:
# Example: block hA1 (10.0.0.1) -> hB1 (10.0.0.5) TCP/80
python3 orchestrator/orchestrator.py \
  push-blocklist --rule '{"src_ip":"10.0.0.1","dst_ip":"10.0.0.5","proto":"tcp","dport":80}'
```
## Validate in Mininet:
```bash
hB1 python3 -m http.server 80 &
hA1 curl -m 2 10.0.0.5:80   # should FAIL (blocked by Child-A)
hA2 curl -m 2 10.0.0.5:80   # should SUCCEED
```

## Failure takeover
```bash
# Start monitor (needs root for ovs-vsctl)
sudo python3 orchestrator/orchestrator.py monitor-failover
# Kill Child-A (Ctrl+C in T1) -> watch auto-rebind of s1a,s2a to master
# In Mininet: pingall   # Site A stays alive via master
# Restart Child-A (T1), then revert:
sudo python3 orchestrator/orchestrator.py rebind --to A --switches s1a,s2a
```