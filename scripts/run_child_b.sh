#!/usr/bin/env bash
#scripts/run_child_b.sh
RYU_APP="controllers/child/child_app.py"
ryu-manager --ofp-tcp-listen-port 6634 $RYU_APP --wsapi-port 8081
