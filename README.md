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