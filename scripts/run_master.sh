#!/usr/bin/env bash
RYU_APP="controllers/master/master_app.py"
ryu-manager --ofp-tcp-listen-port 6653 $RYU_APP
