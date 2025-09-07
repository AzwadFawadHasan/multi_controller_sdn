#!/usr/bin/env bash
#scripts/run_child_a.sh
RYU_APP="controllers/child/child_app.py"
ryu-manager --ofp-tcp-listen-port 6633 $RYU_APP --wsapi-port 8080
