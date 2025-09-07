#!/usr/bin/env bash
# scripts/run_onos_docker.sh
set -e

NAME=onos
IMG=onosproject/onos:2.5.3
REST=http://127.0.0.1:8181
AUTH=onos:rocks

# Clean any old container
docker rm -f "$NAME" 2>/dev/null || true

# Run ONOS (OpenFlow, REST/GUI, CLI)
docker run -d --name "$NAME" \
  -p 6653:6653 \
  -p 8181:8181 \
  -p 8101:8101 \
  "$IMG"

echo "[onos] waiting for REST to come up..."
for i in $(seq 1 40); do
  if curl -su "$AUTH" -m 1 "$REST/onos/v1/applications" >/dev/null 2>&1; then
    echo "[onos] REST is up (try #$i)"
    break
  fi
  sleep 3
  if [ "$i" -eq 40 ]; then
    echo "[onos] REST never became ready"; exit 1
  fi
done

echo "[onos] activating baseline apps..."
# Keep intent/fwd/host/openflow/proxyarp/gui active
for app in openflow hostprovider intent proxyarp fwd gui; do
  curl -su "$AUTH" -sS -X POST \
    "$REST/onos/v1/applications/org.onosproject.${app}/active" >/dev/null || true
done

# Optional: quick, non-fatal verification without jq
echo "[onos] verifying apps (non-fatal)..."
curl -su "$AUTH" -sS "$REST/onos/v1/applications" \
 | grep -E '"name":"org.onosproject\.(openflow|hostprovider|intent|proxyarp|fwd|gui)"' || true

echo "ONOS up. GUI: http://127.0.0.1:8181/onos/ui (user: onos, pass: rocks)"
