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

# PHase 3

## Start  4 terminals :

T1: make childA

T2: make childB

T3: make master

T4: make two_sites

If first pingall drops a few, run pingall again (learning/ARP).

4) Phase-3 tests 
## Baseline cross-site latency / throughput (WAN impairment visible)

In Mininet (T4):

## Round-trip delay will be ~60ms due to 30ms each way + jitter
hA1 ping -c 3 10.0.0.5

## Throughput (install iperf3 if needed): expect lower than Phase-2 due to delay/loss
### On hB1:
hB1 iperf3 -s &
### On hA1 (new Mininet line):
hA1 iperf3 -c 10.0.0.5 -t 5

B) Push a cross-site “intent” (pin A1<->B1 onto the WAN core link)

In a shell (outside Mininet):

python3 orchestrator/orchestrator.py push-crosssite --src 10.0.0.1 --dst 10.0.0.5


Validate flows (any shell):

sudo ovs-ofctl -O OpenFlow13 dump-flows s0a | grep nw_src=10.0.0.1
sudo ovs-ofctl -O OpenFlow13 dump-flows s0b | grep nw_src=10.0.0.1


You should see the priority=3000 entries we added.

Re-run latency / throughput (you won’t see a shorter RTT—this pins path, not physics—but you’ve now got deterministic core egress (port3) for that pair).

C) Global ACL still works alongside cross-site pin
# Start HTTP on B1
# (If it's still running from before, skip starting again)
hB1 python3 -m http.server 80 &

# Block A1 -> B1:80 using the usual global rule
python3 orchestrator/orchestrator.py \
  push-blocklist --rule '{"src_ip":"10.0.0.1","dst_ip":"10.0.0.5","proto":"tcp","dport":80}'

# In Mininet:
hA1 curl -m 2 10.0.0.5:80   # should FAIL
hA2 curl -m 2 10.0.0.5:80   # should SUCCEED

D) Failover (now per-site, same as Phase-2)
# Monitor (needs sudo for ovs-vsctl)
sudo python3 orchestrator/orchestrator.py monitor-failover
# Kill Child-A (Ctrl+C in T1). Watch s1a,s2a rebind to master.
# In Mininet:
pingall
# Restart Child-A (run make childA again),
# then failback (now succeeds without errors, we added sudo in helper):
python3 orchestrator/orchestrator.py rebind --to A --switches s1a,s2a

E) Clear the pinned flows (cleanup)
python3 orchestrator/orchestrator.py clear-crosssite --src 10.0.0.1 --dst 10.0.0.5
sudo ovs-ofctl -O OpenFlow13 dump-flows s0a | grep 10.0.0.1 || echo "cleared on s0a"
sudo ovs-ofctl -O OpenFlow13 dump-flows s0b | grep 10.0.0.1 || echo "cleared on s0b"

#### phase 3 details:
Is a few % packet loss after killing Child-A expected?

Short answer: yes.

In Phase-3 we impaired the WAN link (s0a↔s0b) with loss=1 and jitter/delay. During failover, you also have:

Controller handover: s1a/s2a drop Child-A, bind to Master; flow tables are briefly empty until the Master’s L2 app relearns.

ARP + L2 relearning: the first pings after failover often time out as MACs/flows repopulate.

Those two effects stack with the 1% WAN loss; seeing ~3–5% momentary ping loss right after failover is normal.

After you rebind back to Child-A and the tables settle, ping returns to 0% — exactly what you observed. That’s a good sign.

Did we finish Phase-3?

Yes. Phase-3 goals were:

WAN realism on the inter-site link (delay/jitter/loss).

Cross-site steering (“intent”) by pinning a host pair’s traffic across the core-to-core link.

Cleaner failback (sudo baked into ovs-vsctl in the orchestrator).
You exercised all of these.

What changed from Phase-2 → Phase-3?
Phase-2 (what you had)

Two sites:

Site-A: core s0a → ToRs s1a,s2a → hosts hA1..hA4.

Site-B: core s0b → ToRs s1b,s2b → hosts hB1..hB4.

Children (Ryu): Child-A controls s1a,s2a; Child-B controls s1b,s2b.

Master (Ryu): controls s0a,s0b (and takes over ToRs on failover).

Orchestrator: pushes global ACL to children; detects child failure; rebinds ToRs to master.

Phase-3 (what’s new)

WAN impairment on s0a↔s0b: delay=30ms, jitter=5ms, loss=1%.

Deterministic core ports: we pinned the inter-core link to port 3 on both cores (and set consistent port IDs to ToRs).

Cross-site steering command:

push-crosssite --src 10.0.0.1 --dst 10.0.0.5 installs priority=3000 OpenFlow rules on s0a & s0b to force A↔B traffic out port 3 (the WAN).

clear-crosssite removes those rules.

Failback polish: the orchestrator now calls sudo ovs-vsctl … internally, so rebind --to A --switches s1a,s2a works cleanly after Child-A recovers.

Functionally: Phase-2 proved multi-domain, global policy, and failover. Phase-3 added path control across sites and WAN realism, plus smoother failback.

Your current Phase-3 topology (explicit “who connects to who”)
Site-A

s0a (core, controlled by Master)

port1 ↔ s1a (ToR-A1)

port2 ↔ s2a (ToR-A2)

port3 ↔ s0b (inter-site WAN, impaired)

s1a (ToR-A1, Child-A)

↔ s0a (up)

↔ hA1 (10.0.0.1/24), hA2 (10.0.0.2/24) (down)

s2a (ToR-A2, Child-A)

↔ s0a (up)

↔ hA3 (10.0.0.3/24), hA4 (10.0.0.4/24) (down)

Site-B

s0b (core, controlled by Master)

port1 ↔ s1b (ToR-B1)

port2 ↔ s2b (ToR-B2)

port3 ↔ s0a (inter-site WAN, impaired)

s1b (ToR-B1, Child-B)

↔ s0b (up)

↔ hB1 (10.0.0.5/24), hB2 (10.0.0.6/24) (down)

s2b (ToR-B2, Child-B)

↔ s0b (up)

↔ hB3 (10.0.0.7/24), hB4 (10.0.0.8/24) (down)

Control & orchestration

Child-A (Ryu, 6633) ←→ s1a,s2a

Child-B (Ryu, 6634) ←→ s1b,s2b

Master (Ryu, 6653) ←→ s0a,s0b; plus takes over ToRs on failover.

Orchestrator (Python)

Global ACL to children: /blocklist REST (unchanged).

Cross-site steering: ovs-ofctl rules on s0a,s0b (priority=3000, output:3).

Failover/failback: sudo ovs-vsctl set-controller ….

What’s next (Phase-4 preview)

Swap Master → ONOS (or ODL) for real Intents/FlowObjective, GUI, and optional controller clustering.

Keep Ryu at the edge (children).

Add realism components: LB/DNS/Firewall/IDS and monitoring (sFlow-RT, later Prom/Grafana).

At that point the master behaves as a controller-of-controllers (NB APIs to children), not just another OpenFlow speaker.

# Phase 4
## 1. Make sure ONOS is listening
```bash 
nc -zv 127.0.0.1 6653
```

## 2 Rebind the cores to ONOS + force OF1.3
Run these exactly (Mininet/topo running): (two sites)
```bash
# Show current controller targets
sudo ovs-vsctl get-controller s0a
sudo ovs-vsctl get-controller s0b

# Rebind to ONOS and lock protocol to OpenFlow13
sudo ovs-vsctl del-controller s0a
sudo ovs-vsctl set-controller s0a tcp:127.0.0.1:6653
sudo ovs-vsctl set bridge s0a protocols=OpenFlow13

sudo ovs-vsctl del-controller s0b
sudo ovs-vsctl set-controller s0b tcp:127.0.0.1:6653
sudo ovs-vsctl set bridge s0b protocols=OpenFlow13

# (optional) secure mode so they don’t self-learn without a controller
sudo ovs-vsctl set-fail-mode s0a secure
sudo ovs-vsctl set-fail-mode s0b secure

# Verify OpenFlow handshake works
sudo ovs-ofctl -O OpenFlow13 show s0a
sudo ovs-ofctl -O OpenFlow13 show s0b
```
You should now see the devices in ONOS:
```bash
curl -u onos:rocks http://127.0.0.1:8181/onos/v1/devices
# or in the GUI: Devices should be > 0
```

## 3 Make sure ONOS apps are active (esp. OpenFlow + fwd)
```bash
curl -u onos:rocks http://127.0.0.1:8181/onos/v1/applications | jq '.applications[] | select(.state=="ACTIVE") | .id'
# If needed, activate:
curl -u onos:rocks -X POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.openflow/active
curl -u onos:rocks -X POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.fwd/active
curl -u onos:rocks -X POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.hostprovider/active

```
pingall
