# scripts/run_onos_docker.sh
# !/usr/bin/env bash
# # ONOS in Docker (exposes OpenFlow, REST/GUI, and CLI)
# docker rm -f onos 2>/dev/null || true
# docker run -d --name onos \
#   -p 6653:6653 \    # OpenFlow
#   -p 8181:8181 \    # REST API + GUI (http://localhost:8181/onos/ui/)
#   -p 8101:8101 \    # ONOS CLI (SSH)
#   onosproject/onos:latest

# echo "Waiting 10s for ONOS to boot..."
# sleep 10

# # Activate baseline apps (intent, openflow, host provider, reactive fwd, gui, proxyarp)
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.openflow/active    >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.hostprovider/active >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.intent/active       >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.proxyarp/active     >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.fwd/active          >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.gui/active          >/dev/null

# echo "ONOS up. GUI: http://127.0.0.1:8181/onos/ui (user: onos, pass: rocks)"


#!/usr/bin/env bash
# ONOS in Docker (exposes OpenFlow, REST/GUI, and CLI)
# docker rm -f onos 2>/dev/null || true

# docker run -d --name onos \
#   -p 6653:6653 \
#   -p 8181:8181 \
#   -p 8101:8101 \
#   onosproject/onos:latest

# echo "Waiting 10s for ONOS to boot..."
# sleep 10

# # Activate baseline apps (intent, openflow, host provider, reactive fwd, gui, proxyarp)
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.openflow/active    >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.hostprovider/active >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.intent/active       >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.proxyarp/active     >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.fwd/active          >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.gui/active          >/dev/null

# echo "ONOS up. GUI: http://127.0.0.1:8181/onos/ui (user: onos, pass: rocks)"




# #!/usr/bin/env bash
# docker rm -f onos 2>/dev/null || true
# docker run -d --name onos \
#     -p 6653:6653 -p 8181:8181 -p 8101:8101 \
#     onosproject/onos:2.7.0

# echo "Waiting 20s for ONOS to boot..."
# sleep 20

# # Activate key ONOS apps
# for app in openflow hostprovider intent proxyarp fwd gui; do
#     curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.${app}/active >/dev/null
# done

# echo "ONOS up. GUI: http://127.0.0.1:8181/onos/ui (user: onos, pass: rocks)"




#!/usr/bin/env bash
# ONOS in Docker (exposes OpenFlow, REST/GUI, and CLI)
# docker rm -f onos 2>/dev/null || true

# docker run -d --name onos \
#   -p 6653:6653 \
#   -p 8181:8181 \
#   -p 8101:8101 \
#   onosproject/onos:latest

# echo "Waiting 10s for ONOS to boot..."
# sleep 2

# # Activate baseline apps (intent, openflow, host provider, reactive fwd, gui, proxyarp)
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.openflow/active    >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.hostprovider/active >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.intent/active       >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.proxyarp/active     >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.fwd/active          >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.gui/active          >/dev/null

# echo "ONOS up. GUI: http://127.0.0.1:8181/onos/ui (user: onos, pass: rocks)"





# 0) Stop/replace any running ONOS
# docker rm -f onos 2>/dev/null || true

# # 1) Pull a release that still bundles Intents (2.5.3 works well)
# docker pull onosproject/onos:2.5.3

# # 2) Run it
# docker run -d --name onos \
#   -p 6653:6653 -p 8181:8181 -p 8101:8101 \
#   onosproject/onos:2.5.3

# # 3) Give it a little time to boot
# sleep 15

# # 4) Activate the baseline apps (idempotent; safe to repeat)
# for app in openflow hostprovider intent proxyarp fwd gui; do
#   curl -u onos:rocks -sS -X POST \
#     http://127.0.0.1:8181/onos/v1/applications/org.onosproject.$app/active > /dev/null
# done

# # 5) Confirm 'intent' is truly ACTIVE
# curl -u onos:rocks -sS http://127.0.0.1:8181/onos/v1/applications \
# | jq '.applications[] | select(.name=="org.onosproject.intent") | {name,state}'





#!/usr/bin/env bash
#!/usr/bin/env bash
# set -e

# docker rm -f onos 2>/dev/null || true

# docker run -d --name onos \
#   -p 6653:6653 \
#   -p 8181:8181 \
#   -p 8101:8101 \
#   onosproject/onos:2.5.3

# echo "[onos] waiting for REST to come up..."
# # Loop up to ~120s until REST is ready
# for i in $(seq 1 40); do
#   if curl -u onos:rocks -sS http://127.0.0.1:8181/onos/v1/applications >/dev/null 2>&1; then
#     echo "[onos] REST is up (try #$i)"
#     break
#   fi
#   sleep 3
#   if [ "$i" -eq 40 ]; then
#     echo "[onos] REST never became ready"; exit 1
#   fi
# done

# echo "[onos] activating baseline apps..."
# for app in openflow hostprovider intent proxyarp fwd gui; do
#   curl -u onos:rocks -sS -X POST \
#     "http://127.0.0.1:8181/onos/v1/applications/org.onosproject.${app}/active" >/dev/null || true
# done

# echo "[onos] verifying intent app..."
# curl -u onos:rocks -sS http://127.0.0.1:8181/onos/v1/applications \
# | grep -A2 org.onosproject.intent || echo "[warn] intent app not found"

# echo "ONOS up. GUI: http://127.0.0.1:8181/onos/ui (user: onos, pass: rocks)"





#!/usr/bin/env bash
# set -euo pipefail

# NAME=onos
# IMG=${IMG:-onosproject/onos:2.2.2}   # lock to a known-good tag
# REST=http://127.0.0.1:8181
# AUTH=onos:rocks

# # Clean any old container
# docker rm -f "$NAME" 2>/dev/null || true

# # Run ONOS (OpenFlow, REST/GUI, CLI)
# docker run -d --name "$NAME" \
#   -p 6653:6653 \
#   -p 8181:8181 \
#   -p 8101:8101 \
#   "$IMG"

# echo "[onos] waiting for REST to come up..."
# for i in {1..30}; do
#   if curl -su "$AUTH" -m 1 "$REST/onos/v1/applications" >/dev/null 2>&1; then
#     echo "[onos] REST is up (try #$i)"
#     break
#   fi
#   sleep 1
#   if [[ $i -eq 30 ]]; then
#     echo "[onos] REST did not come up in time"; exit 1
#   fi
# done

# echo "[onos] activating baseline apps..."
# # NOTE: do NOT try to activate org.onosproject.intent (it doesn't exist)
# for app in openflow hostprovider proxyarp fwd gui gui2; do
#   curl -su "$AUTH" -sS -X POST \
#     "$REST/onos/v1/applications/org.onosproject.$app/active" >/dev/null || true
# done

# echo "[onos] verifying..."
# curl -su "$AUTH" "$REST/onos/v1/applications" | jq -r '
#   .applications[] | select(.state=="ACTIVE") | .name' | sort

# echo 'ONOS up. GUI: http://127.0.0.1:8181/onos/ui (user: onos, pass: rocks)'


#!/usr/bin/env bash
# ONOS in Docker (exposes OpenFlow, REST/GUI, and CLI)
# docker rm -f onos 2>/dev/null || true

# docker run -d --name onos \
#   -p 6653:6653 \
#   -p 8181:8181 \
#   -p 8101:8101 \
#   onosproject/onos:2.5.3

# echo "Waiting 15s for ONOS to boot..."
# sleep 15

# # Activate baseline apps (openflow, host provider, proxyarp, fwd, gui)
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.openflow/active    >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.hostprovider/active >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.proxyarp/active     >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.fwd/active          >/dev/null
# curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.gui/active          >/dev/null

# echo "ONOS up. GUI: http://127.0.0.1:8181/onos/ui (user: onos, pass: rocks)"









#!/usr/bin/env bash
# ONOS in Docker (exposes OpenFlow, REST/GUI, and CLI)
docker rm -f onos 2>/dev/null || true

docker run -d --name onos \
  -p 6653:6653 \
  -p 8181:8181 \
  -p 8101:8101 \
  onosproject/onos:latest

echo "Waiting 15s for ONOS to boot..."
sleep 15
# in scripts/run_onos_docker.sh, after `docker run ...`
echo "Waiting for ONOS REST..."
for i in {1..60}; do
  if curl -su onos:rocks -m 1 http://127.0.0.1:8181/onos/v1/applications >/dev/null 2>&1; then
    echo "ONOS REST is up (try #$i)"; break
  fi
  sleep 1
done

# Activate baseline apps (intent, openflow, host provider, reactive fwd, gui, proxyarp)
curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.openflow/active    >/dev/null
curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.hostprovider/active >/dev/null
curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.intent/active       >/dev/null
curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.proxyarp/active     >/dev/null
curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.fwd/active          >/dev/null
curl -u onos:rocks -sSX POST http://127.0.0.1:8181/onos/v1/applications/org.onosproject.gui/active          >/dev/null

echo "ONOS up. GUI: http://127.0.0.1:8181/onos/ui (user: onos, pass: rocks)"
