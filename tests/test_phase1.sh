#!/usr/bin/env bash
set -euo pipefail

echo "[TEST] Phase-1 requires controllers and topo already running in separate terminals."
echo "Steps:"
echo "1) In term-1: make childA"
echo "2) In term-2: make childB"
echo "3) In term-3: make master"
echo "4) In term-4: make topo"
echo "Then run the commands below in a 5th terminal as you read the output."

echo "[TEST] Health checks"
python3 orchestrator/orchestrator.py health || true

echo "[TEST] Global blocklist (hA1 -> hB1 tcp/80)"
python3 orchestrator/orchestrator.py push-blocklist --rule '{"src_ip":"10.0.1.1","dst_ip":"10.0.2.1","proto":"tcp","dport":80}'

echo "[NEXT] In Mininet CLI, try:"
echo "  hB1 python3 -m http.server 80 &"
echo "  hA1 curl -m 2 10.0.2.1:80   # should FAIL due to blocklist"
echo "  hA2 curl -m 2 10.0.2.1:80   # should work (not blocked)"
echo
echo "[TEST] Failover demo:"
echo "  Kill Child-A terminal (Ctrl+C)."
echo "  In this terminal run: python3 orchestrator/orchestrator.py monitor-failover"
echo "  It will rebind s1 -> master automatically."
echo "  In Mininet CLI, run: pingall  # A-domain keeps working via master."
echo "  Restart Child-A, then rebind back:"
echo "      python3 orchestrator/orchestrator.py rebind --to A --switches s1"
