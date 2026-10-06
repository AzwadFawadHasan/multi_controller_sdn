# Multi-Controller SDN — Hierarchical Control with Ryu, ONOS, Mininet & Open vSwitch

![Visitor Count](https://visitor-badge.laobi.icu/badge?page_id=AzwadFawadHasan.multi_controller_sdn)

A hierarchical Software-Defined Networking testbed that evolves from a single-site Ryu deployment to a two-site, WAN-impaired, ONOS-orchestrated multi-domain network.

Built with **Mininet, Open vSwitch (OpenFlow 1.3), Ryu, ONOS, and a custom Python orchestrator** — demonstrating global policy enforcement, cross-site traffic steering, and controller failover/failback.

![Topology](https://github.com/user-attachments/assets/a4d07eb9-eb20-484e-a20e-c7583717acb8)

> **For recruiters / supervisors:** start with **Overview + Architecture + How to run (Phase 1)** below. Advanced phases live on separate branches — see [Branches & Phases](#-branches--phases).

--- 

## Overview

Traditional single-controller SDN doesn't scale across sites and is a single point of failure. This project implements a **controller-of-controllers** hierarchy:

- **Child controllers (Ryu)** own their local site's ToR switches and enforce L2 learning + ACLs via REST.
- **Master controller (Ryu → ONOS)** owns the inter-site core switches.
- **Orchestrator (Python CLI)** pushes global policy to children, steers cross-site traffic, and rebinds switches on failure.

Single `/24` (`10.0.0.0/24`) is used throughout for simplicity.

## Architecture

```
                +------------------+
                |   Orchestrator   |  health / push-blocklist /
                |  (Python CLI)    |  push-crosssite / monitor-failover /
                +---+----------+---+  rebind / onos-* (Phase 4)
                    |          |
        REST :8080/8081       |  ONOS REST :8181 (Phase 4)
                    |          |
        +-----------+          +----------------+
        |                                     |
  Child-A (Ryu :6633)  Child-B (Ryu :6634)  Master (Ryu :6653 → ONOS :6653)
   s1a, s2a (Site A ToRs)  s1b, s2b (Site B ToRs)  s0a, s0b (Site cores)
        |                                     |
  hA1-hA4 (10.0.0.1-4)   hB1-hB4 (10.0.0.5-8)   s0a <-> s0b WAN (Phase 3+: 30ms / 5ms jitter / 1% loss)
```

**Control mapping (final, Phase 2+):**

| Controller | Type | Port | Switches |
|---|---|---|---|
| Child-A | Ryu `ChildL2Acl` | 6633 / REST 8080 | `s1a`, `s2a` |
| Child-B | Ryu `ChildL2Acl` | 6634 / REST 8081 | `s1b`, `s2b` |
| Master | Ryu `master_app` → ONOS 2.5.3 | 6653 / REST 8181 | `s0a`, `s0b` (+ ToRs on failover) |

**Key mechanisms:**

- L2 learning switch + high-priority `DROP` ACL flows (`priority=2000`) on children
- Deterministic core ports (`port 3` = WAN) + pinned steering flows (`priority=3000`) on cores
- Failover via `ovs-vsctl set-controller` — ToRs rebound to master when a child dies
- Phase 4: ONOS `PointToPointIntent` with IPv4 selectors instead of raw `ovs-ofctl` flows

## Tech Stack

- **Emulation:** Mininet, Open vSwitch, `TCLink`
- **Controllers:** Ryu (`ryu-manager`), ONOS 2.5.3 (Docker)
- **Protocols:** OpenFlow 1.3, LLDP (filtered), ARP, ICMP, TCP/HTTP, iperf3
- **Orchestration:** Python (`requests`, `pyyaml`, `ovs-vsctl` / `ovs-ofctl` wrappers)
- **Validation:** `pingall`, `curl`, `iperf3`, `ovs-ofctl dump-flows`, ONOS REST/GUI

## Project Structure

```
multi_controller_sdn/
├── topo/
│   ├── tiny_two_clusters.py   # Phase 1: single-site (s0, s1, s2 + 4 hosts)
│   └── two_sites_small.py     # Phase 2+: two sites (s0a/s1a/s2a + s0b/s1b/s2b + 8 hosts)
├── controllers/
│   ├── child/child_app.py     # Ryu L2 + REST (/health, /stats, /blocklist)
│   └── master/master_app.py   # Ryu L2 core (standalone, no WSGI)
├── orchestrator/
│   ├── orchestrator.py        # CLI: health, blocklist, failover, cross-site, ONOS
│   └── config.yaml            # controller IPs/ports + switch ownership
├── scripts/
│   ├── run_child_a.sh         # Ryu Child-A :6633 / :8080
│   ├── run_child_b.sh         # Ryu Child-B :6634 / :8081
│   ├── run_master.sh          # Ryu Master :6653
│   ├── run_topo.sh            # single-site topo
│   ├── run_topo_two_sites.sh  # two-site topo (Phase 2+)
│   └── run_onos_docker.sh     # ONOS 2.5.3 container (Phase 4)
├── tests/
│   └── test_phase1.sh         # guided Phase-1 checklist
└── Makefile                   # make childA / childB / master / topo / two_sites / onos
```

## Branches & Phases

This repo was developed incrementally. `main` holds the stable Phase-1 baseline; later phases are preserved on branches:

| Branch | Phase | What it adds |
|---|---|---|
| `main` | **Phase 1 — Single-site baseline** | 3-switch topo, Ryu child+master, global blocklist, failover monitor/rebind |
| `origin/2nd_phase` | **Phase 2 — Two-site multi-domain** | 6-switch / 8-host topo, per-site ownership, cross-domain ACL + per-site failover |
| `origin/3rd_phase` | **Phase 3 — WAN + steering intent** | 30ms/jitter/loss WAN, deterministic port 3, `push-crosssite` / `clear-crosssite` (OVS flows), sudo-polished failback |
| `origin/4th_phase` | **Phase 4 — ONOS master + intents** | ONOS replaces Ryu master, Docker bootstrap, `onos-*` CLI, `PointToPointIntent`, working failover on ONOS cores |

```bash
git fetch --all
git branch -a

# check out a phase:
git switch -c 2nd_phase origin/2nd_phase
# or: git checkout 2nd_phase
```

> The instructions below describe **Phase 1 on `main`**. Per-phase deltas and commands follow in [Phase 2 → 4](#-phase-2--4-deltas).

## Prerequisites

- Ubuntu + Mininet + Open vSwitch (`sudo mn --test pingall` works)
- Python 3, `ryu-manager`, `pip install requests pyyaml webob`
- For Phase 4: Docker + `curl`, `jq` (optional)
- Make scripts executable once: `chmod +x scripts/*.sh`

Clean stale state before any run:

```bash
sudo mn -c
pkill -f ryu-manager || true
sudo ovs-vsctl del-br s0 s1 s2 s0a s0b s1a s2a s1b s2b 2>/dev/null || true
```

> First `pingall` often drops packets — run `pingall` a second time. This is expected ARP + L2 learning, not a bug. Once tables populate, loss goes to 0%.

## How to Run (Phase 1 — `main`)

Open 4 terminals (only Mininet needs `sudo`):

| Term | Command | What it starts |
|---|---|---|
| T1 | `make childA` | Ryu Child-A (`:6633`, REST `:8080`) → `s1` |
| T2 | `make childB` | Ryu Child-B (`:6634`, REST `:8081`) → `s2` |
| T3 | `make master` | Ryu Master (`:6653`) → `s0` |
| T4 | `make topo` | Mininet `tiny_two_clusters.py` (hA1 `.1`, hA2 `.2` on `s1`; hB1 `.3`, hB2 `.4` on `s2`) |

### 1. Health check

```bash
python3 orchestrator/orchestrator.py health
# or:
curl -s http://127.0.0.1:8080/health; echo
curl -s http://127.0.0.1:8081/health; echo
```

### 2. Global blocklist

Push once from the orchestrator — it fans out to **both** children:

```bash
python3 orchestrator/orchestrator.py \
  push-blocklist --rule '{"src_ip":"10.0.0.1","dst_ip":"10.0.0.3","proto":"tcp","dport":80}'
```

Validate inside Mininet (T4):

```bash
hB1 python3 -m http.server 80 &
hA1 curl -m 2 10.0.0.3:80   # should FAIL (blocked)
hA2 curl -m 2 10.0.0.3:80   # should SUCCEED (not blocked)
```

### 3. Failover / failback

```bash
# T5 (needs sudo for ovs-vsctl):
sudo python3 orchestrator/orchestrator.py monitor-failover
```

1. Kill Child-A (`Ctrl+C` in T1)
2. Watch `s1` auto-rebind to master; in Mininet run `pingall` — Site A stays up via master
3. Restart Child-A (`make childA`), then fail back:
```bash
sudo python3 orchestrator/orchestrator.py rebind --to A --switches s1
```

A guided checklist is also in `tests/test_phase1.sh` and `make test_b`.

## Phase 2 → 4 Deltas

### Phase 2 — Two-site (`origin/2nd_phase`)

- New topo `two_sites_small.py`: `s0a→s1a,s2a` (Site A: `hA1-hA4` `.1-.4`), `s0b→s1b,s2b` (Site B: `hB1-hB4` `.5-.8`); cores on master, ToRs on respective child.
- `config.yaml` now maps `A → [s1a,s2a]`, `B → [s1b,s2b]`, `cores: [s0a,s0b]`.
- Run with `make two_sites` instead of `make topo`.

```bash
make childA && make childB && make master  # T1-T3
make two_sites                              # T4
python3 orchestrator/orchestrator.py health
python3 orchestrator/orchestrator.py \
  push-blocklist --rule '{"src_ip":"10.0.0.1","dst_ip":"10.0.0.5","proto":"tcp","dport":80}'
# Mininet: hB1 python3 -m http.server 80 & ; hA1 curl -m 2 10.0.0.5:80 # FAIL ; hA2 curl ... # OK
sudo python3 orchestrator/orchestrator.py monitor-failover  # kill Child-A → s1a,s2a → master
sudo python3 orchestrator/orchestrator.py rebind --to A --switches s1a,s2a
```

### Phase 3 — WAN realism + steering (`origin/3rd_phase`)

- WAN link `s0a↔s0b` impaired: `delay='30ms', jitter='5ms', loss=1`; pinned to `port 3` on both cores.
- New orchestrator commands using `ovs-ofctl` (`priority=3000`):
  - `push-crosssite --src 10.0.0.1 --dst 10.0.0.5`
  - `clear-crosssite --src 10.0.0.1 --dst 10.0.0.5`
- Failback now embeds `sudo ovs-vsctl` so `rebind` works without manual sudo wrangling.

```bash
hA1 ping -c 3 10.0.0.5                    # ~60ms RTT (30ms each way)
hB1 iperf3 -s & ; hA1 iperf3 -c 10.0.0.5 -t 5
python3 orchestrator/orchestrator.py push-crosssite --src 10.0.0.1 --dst 10.0.0.5
sudo ovs-ofctl -O OpenFlow13 dump-flows s0a | grep nw_src=10.0.0.1
sudo ovs-ofctl -O OpenFlow13 dump-flows s0b | grep nw_src=10.0.0.1
python3 orchestrator/orchestrator.py clear-crosssite --src 10.0.0.1 --dst 10.0.0.5
```

> A few % loss right after killing Child-A is expected: controller handover + ARP/L2 relearning stacked on the 1% WAN loss. After rebind + settle, `pingall` returns to 0%.

### Phase 4 — ONOS master (`origin/4th_phase`)

- Master moves from Ryu to **ONOS 2.5.3** (Docker, `:6653` OpenFlow, `:8181` REST/GUI, `:8101` CLI).
- Ryu children stay at the edge; ONOS owns `s0a/s0b` and exposes real intents.
- New: `scripts/run_onos_docker.sh`, `make onos`, `make two_sites`, and orchestrator `onos-*` commands.

```bash
make onos                                   # boots ONOS, activates openflow/hostprovider/intent/proxyarp/fwd/gui
nc -zv 127.0.0.1 6653
# with topo running, rebind cores to ONOS + lock OF1.3:
sudo ovs-vsctl set-controller s0a tcp:127.0.0.1:6653
sudo ovs-vsctl set-controller s0b tcp:127.0.0.1:6653
sudo ovs-vsctl set bridge s0a protocols=OpenFlow13
sudo ovs-vsctl set bridge s0b protocols=OpenFlow13
sudo ovs-vsctl set-fail-mode s0a secure
sudo ovs-vsctl set-fail-mode s0b secure

curl -u onos:rocks http://127.0.0.1:8181/onos/v1/devices
# GUI: http://127.0.0.1:8181/onos/ui (onos / rocks)

python3 orchestrator/orchestrator.py onos-devices
python3 orchestrator/orchestrator.py onos-links
python3 orchestrator/orchestrator.py onos-add-ptp --help
python3 orchestrator/orchestrator.py onos-intents
```

Failover in Phase 4 follows the same `monitor-failover` / `rebind` flow and was verified working against ONOS cores.

## Results

- **Phase 1:** `pingall` 0% after learning; selective `hA1→hB1:80` deny with `hA2` unaffected; kill-Child-A → master takeover with no sustained outage.
- **Phase 2:** Same guarantees across two sites / 8 hosts; per-site failover (`s1a,s2a` → master).
- **Phase 3:** Cross-site RTT ~60ms under impairment; deterministic WAN egress verified via `dump-flows`; transient ~3–5% loss during handover, 0% after failback.
- **Phase 4:** ONOS discovers `s0a/s0b`, intents installable via REST, edge Ryu policy + ONOS core coexist.

## Troubleshooting

- `pingall` drops first run → run `pingall` again (ARP/learning).
- `ryu-manager` won't start → `pkill -f ryu-manager; sudo mn -c` and retry.
- `ovs-vsctl` permission denied → prefix orchestrator `monitor-failover` / `rebind` with `sudo`.
- ONOS REST down → `docker logs onos`, wait ~30–60s, confirm `curl -su onos:rocks http://127.0.0.1:8181/onos/v1/applications`.
- Flows not visible → confirm `protocols=OpenFlow13` and `ovs-ofctl -O OpenFlow13 show s0a`.

## Author

**Azwad Fawad Hasan** — SDN / multi-controller emulation, Ryu + ONOS, Mininet/OpenFlow.

## License

MIT — see `LICENSE`.
