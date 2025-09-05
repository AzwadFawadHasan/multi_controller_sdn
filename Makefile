PY=python3

.PHONY: venv deps up down childA childB master topo orch test_b

deps:
	$(PY) -m pip install -r requirements.txt

childA:
	./scripts/run_child_a.sh

childB:
	./scripts/run_child_b.sh

master:
	./scripts/run_master.sh

topo:
	./scripts/run_topo.sh

orch:
	$(PY) orchestrator/orchestrator.py health

up: deps
	@echo "Open 4 terminals and run: make childA | make childB | make master | make topo"

down:
	sudo mn -c

test_b:
	bash tests/test_phase1.sh
