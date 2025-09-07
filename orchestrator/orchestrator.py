# #!/usr/bin/env python3
# # orchestrator/orchestrator.py
# import argparse, time, subprocess, sys, json, requests, yaml, os

# HERE = os.path.dirname(os.path.abspath(__file__))

# import requests

# ONOS = {"host": "127.0.0.1", "user": "onos", "pass": "rocks"}  # REST defaults

# def onos_url(path):
#     return f"http://{ONOS['host']}:8181{path}"

# def onos_get(path):
#     r = requests.get(onos_url(path), auth=(ONOS['user'], ONOS['pass']), timeout=3)
#     r.raise_for_status()
#     return r.json()

# def onos_post(path, payload, app_id="org.fahad.demo"):
#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "application/json",
#         "X-ONOS-Application-Id": app_id
#     }
#     r = requests.post(onos_url(path), json=payload,
#                       auth=(ONOS['user'], ONOS['pass']),
#                       headers=headers, timeout=3)
#     r.raise_for_status()
#     return r.json() if r.text else {"ok": True}

# def onos_add_ptp_intent(ing_dev, ing_port, eg_dev, eg_port, src_ip, dst_ip,
#                         priority=30000, app_id="org.fahad.demo"):
#     payload = {
#         "type": "PointToPointIntent",
#         "appId": app_id,  # required by ONOS 2.5.x
#         "priority": priority,
#         "ingressPoint": {"device": ing_dev, "port": str(ing_port)},
#         "egressPoint": {"device": eg_dev, "port": str(eg_port)},
#         "selector": {"criteria": [
#             {"type": "ETH_TYPE", "ethType": "0x0800"},
#             {"type": "IPV4_SRC", "ip": f"{src_ip}/32"},
#             {"type": "IPV4_DST", "ip": f"{dst_ip}/32"}
#         ]}
#     }
#     onos_post("/onos/v1/intents", payload, app_id=app_id)
#     print("[ONOS] PointToPointIntent installed")


# def onos_delete(path, app_id="org.fahad.demo"):
#     headers = {
#         "Accept": "application/json",
#         "X-ONOS-Application-Id": app_id
#     }
#     r = requests.delete(onos_url(path),
#                         auth=(ONOS['user'], ONOS['pass']),
#                         headers=headers, timeout=3)
#     r.raise_for_status()
#     return r.json() if r.text else {"ok": True}

# def onos_withdraw_intent(key):
#     onos_delete(f"/onos/v1/intents/{key}")
#     print(f"[ONOS] intent {key} withdrawn")

# def onos_add_ptp_intent(ing_dev, ing_port, eg_dev, eg_port, src_ip, dst_ip,
#                         priority=30000, app_id="org.fahad.demo"):
#     payload = {
#         "type": "PointToPointIntent",
#         "appId": app_id,  # << required on ONOS 2.5.x
#         "priority": priority,
#         "ingressPoint": {"device": ing_dev, "port": str(ing_port)},
#         "egressPoint": {"device": eg_dev, "port": str(eg_port)},
#         "selector": {
#             "criteria": [
#                 {"type": "ETH_TYPE", "ethType": "0x0800"},
#                 {"type": "IPV4_SRC", "ip": f"{src_ip}/32"},
#                 {"type": "IPV4_DST", "ip": f"{dst_ip}/32"}
#             ]
#         }
#     }
#     onos_post("/onos/v1/intents", payload, app_id=app_id)  # << pass it here
#     print("[ONOS] PointToPointIntent installed")



# def onos_list_devices(_=None):
#     js = onos_get("/onos/v1/devices")
#     for d in js.get("devices", []):
#         print(d["id"], d["type"], d["available"])
#     print("\nTip: use 'onos-links' to see the s0a<->s0b link ports.")

# def onos_list_links(_=None):
#     js = onos_get("/onos/v1/links")
#     for l in js.get("links", []):
#         print(f"{l['src']['device']}/{l['src']['port']} <-> {l['dst']['device']}/{l['dst']['port']} ({l['state']})")

# def onos_add_ptp_intent(ing_dev, ing_port, eg_dev, eg_port, src_ip, dst_ip, priority=30000, app_id="org.fahad.demo"):
#     payload = {
#         "type": "PointToPointIntent",
#         "appId": app_id,
#         "priority": priority,
#         "ingressPoint": {"device": ing_dev, "port": str(ing_port)},
#         "egressPoint": {"device": eg_dev, "port": str(eg_port)},
#         "selector": {
#             "criteria": [
#                 {"type": "ETH_TYPE", "ethType": "0x0800"},
#                 {"type": "IPV4_SRC", "ip": f"{src_ip}/32"},
#                 {"type": "IPV4_DST", "ip": f"{dst_ip}/32"}
#             ]
#         }
#     }
#     onos_post("/onos/v1/intents", payload)
#     print("[ONOS] PointToPointIntent installed")

# def onos_list_intents(_=None):
#     js = onos_get("/onos/v1/intents")
#     for it in js.get("intents", []):
#         print(it.get("key"), it.get("type"), it.get("state"))

# def onos_withdraw_intent(key):
#     onos_delete(f"/onos/v1/intents/{key}", app_id="org.fahad.demo")
#     print(f"[ONOS] intent {key} withdrawn")



# def load_cfg():
#     with open(os.path.join(HERE, 'config.yaml'), 'r') as f:
#         return yaml.safe_load(f)

# def curl_child(child, path, method='GET', payload=None, timeout=2):
#     base = f"http://{child['ip']}:{child['rest_port']}{path}"
#     if method == 'GET':
#         r = requests.get(base, timeout=timeout)
#     else:
#         r = requests.post(base, json=payload, timeout=timeout)
#     r.raise_for_status()
#     return r.json()

# # def ovs_set_controller(sw, target):
# #     # target: "tcp:IP:PORT"
# #     cmd = ['ovs-vsctl', 'set-controller', sw, target]
# #     subprocess.check_call(cmd)

# def ovs_set_controller(sw, target):
#     cmd = ['sudo', 'ovs-vsctl', 'set-controller', sw, target]
#     subprocess.check_call(cmd)
# def ofctl_add_flow(sw, flow):
#     # Always use OpenFlow 1.3 to match Ryu apps
#     cmd = ['sudo', 'ovs-ofctl', '-O', 'OpenFlow13', 'add-flow', sw, flow]
#     subprocess.check_call(cmd)

# def ofctl_del_flow_strict(sw, flow):
#     cmd = ['sudo', 'ovs-ofctl', '-O', 'OpenFlow13', '--strict', 'del-flows', sw, flow]
#     subprocess.check_call(cmd)

# def push_crosssite(src_ip, dst_ip):
#     """
#     Pin traffic src_ip -> dst_ip across the inter-core link only.
#     We install high-priority ip matches on s0a and s0b to always egress via port3.
#     (Return path is pinned too.)
#     """
#     # A->B on s0a: send towards WAN (port3)
#     ofctl_add_flow('s0a', f'priority=3000,ip,nw_src={src_ip},nw_dst={dst_ip},actions=output:3')
#     # A<-B on s0a (return towards site A over WAN)
#     ofctl_add_flow('s0a', f'priority=3000,ip,nw_src={dst_ip},nw_dst={src_ip},actions=output:3')

#     # On s0b do the symmetric pin across WAN
#     ofctl_add_flow('s0b', f'priority=3000,ip,nw_src={src_ip},nw_dst={dst_ip},actions=output:3')
#     ofctl_add_flow('s0b', f'priority=3000,ip,nw_src={dst_ip},nw_dst={src_ip},actions=output:3')

# def clear_crosssite(src_ip, dst_ip):
#     # remove the 4 flows we added
#     ofctl_del_flow_strict('s0a', f'priority=3000,ip,nw_src={src_ip},nw_dst={dst_ip}')
#     ofctl_del_flow_strict('s0a', f'priority=3000,ip,nw_src={dst_ip},nw_dst={src_ip}')
#     ofctl_del_flow_strict('s0b', f'priority=3000,ip,nw_src={src_ip},nw_dst={dst_ip}')
#     ofctl_del_flow_strict('s0b', f'priority=3000,ip,nw_src={dst_ip},nw_dst={src_ip}')


# def health(args):
#     cfg = load_cfg()
#     for name, child in cfg['children'].items():
#         try:
#             js = curl_child(child, '/health')
#             print(f"[{name}] OK {js}")
#         except Exception as e:
#             print(f"[{name}] DOWN ({e})")

# def push_blocklist(args):
#     cfg = load_cfg()
#     rule = json.loads(args.rule)
#     for name, child in cfg['children'].items():
#         try:
#             js = curl_child(child, '/blocklist', method='POST', payload=rule)
#             print(f"[{name}] applied: {js.get('applied')}")
#         except Exception as e:
#             print(f"[{name}] ERROR applying blocklist: {e}")
#             # still proceed to others

# def monitor_failover(args):
#     cfg = load_cfg()
#     master = cfg['master']
#     target_master = f"tcp:{master['ip']}:{master['of_port']}"
#     backoff = 0.5
#     print("[orchestrator] monitoring children for failover... Ctrl+C to stop")
#     while True:
#         for name, child in cfg['children'].items():
#             try:
#                 curl_child(child, '/health', timeout=1.0)
#                 # healthy? if this child's switches currently point to master, return them
#                 # (we keep it simple; you could query ovs-vsctl get-controller to decide)
#             except Exception:
#                 print(f"[FAILOVER] {name} appears DOWN → rebind its switches to MASTER")
#                 for sw in child['switches']:
#                     ovs_set_controller(sw, target_master)
#         time.sleep(backoff)

# def rebind(args):
#     cfg = load_cfg()
#     master = cfg['master']
#     target = None
#     if args.to == 'master':
#         target = f"tcp:{master['ip']}:{master['of_port']}"
#     else:
#         # args.to is child key: A or B
#         child = cfg['children'][args.to]
#         target = f"tcp:{child['ip']}:{child['of_port']}"
#     for sw in args.switches.split(','):
#         sw = sw.strip()
#         if sw:
#             print(f"[rebind] {sw} -> {target}")
#             ovs_set_controller(sw, target)




# def main():
#     ap = argparse.ArgumentParser(prog='orchestrator')
#     sub = ap.add_subparsers(dest='cmd')

#     s1 = sub.add_parser('health', help='check /health on children')
#     s1.set_defaults(func=health)

#     s2 = sub.add_parser('push-blocklist', help='push global blocklist rule (JSON string)')
#     s2.add_argument('--rule', required=True, help='JSON rule, e.g. {"src_ip":"10.0.1.1","dst_ip":"10.0.2.1","proto":"tcp","dport":80}')
#     s2.set_defaults(func=push_blocklist)

#     s3 = sub.add_parser('monitor-failover', help='monitor children, rebind dead child switches to master')
#     s3.set_defaults(func=monitor_failover)

#     s4 = sub.add_parser('rebind', help='manually rebind switches')
#     s4.add_argument('--to', required=True, choices=['master','A','B'])
#     s4.add_argument('--switches', required=True, help='comma-separated switch names, e.g., s1 or s1,s2')
#     s4.set_defaults(func=rebind)

#     s5 = sub.add_parser('push-crosssite', help='pin A<->B traffic across WAN (cores port3)')
#     s5.add_argument('--src', required=True, help='source IP (e.g., 10.0.0.1)')
#     s5.add_argument('--dst', required=True, help='dest IP (e.g., 10.0.0.5)')
#     def _pc(args): push_crosssite(args.src, args.dst)
#     s5.set_defaults(func=_pc)

#     s6 = sub.add_parser('clear-crosssite', help='remove pinned A<->B WAN flows')
#     s6.add_argument('--src', required=True)
#     s6.add_argument('--dst', required=True)
#     def _cc(args): clear_crosssite(args.src, args.dst)
#     s6.set_defaults(func=_cc)
#     s7 = sub.add_parser('onos-devices', help='list ONOS devices')
#     s7.set_defaults(func=onos_list_devices)

#     s8 = sub.add_parser('onos-links', help='list ONOS links')
#     s8.set_defaults(func=onos_list_links)

#     s9 = sub.add_parser('onos-add-ptp', help='add a PointToPointIntent with IPv4 selector')
#     s9.add_argument('--ing-dev', required=True)
#     s9.add_argument('--ing-port', required=True, type=int)
#     s9.add_argument('--eg-dev', required=True)
#     s9.add_argument('--eg-port', required=True, type=int)
#     s9.add_argument('--src', required=True, help='IPv4 src (e.g., 10.0.0.1)')
#     s9.add_argument('--dst', required=True, help='IPv4 dst (e.g., 10.0.0.5)')
#     def _ap(args): onos_add_ptp_intent(args.ing_dev, args.ing_port, args.eg_dev, args.eg_port, args.src, args.dst)
#     s9.set_defaults(func=_ap)

#     s10 = sub.add_parser('onos-intents', help='list intents')
#     s10.set_defaults(func=onos_list_intents)

#     s11 = sub.add_parser('onos-del', help='withdraw intent by key')
#     s11.add_argument('--key', required=True)
#     def _od(args): onos_withdraw_intent(args.key)
#     s11.set_defaults(func=_od)



#     args = ap.parse_args()
#     if not hasattr(args, 'func'):
#         ap.print_help(); sys.exit(1)
#     args.func(args)

# if __name__ == '__main__':
#     main()







#!/usr/bin/env python3
# orchestrator/orchestrator.py

import argparse, time, subprocess, sys, json, requests, yaml, os

HERE = os.path.dirname(os.path.abspath(__file__))

# ONOS REST defaults
ONOS = {"host": "127.0.0.1", "user": "onos", "pass": "rocks"}
# Use an installed ONOS app as the Application-Id (header + JSON).
# We pick org.onosproject.fwd since you activate it on startup.
DEFAULT_APP_ID = "org.onosproject.fwd"

# ------------- ONOS REST helpers -------------
def onos_url(path: str) -> str:
    return f"http://{ONOS['host']}:8181{path}"

def onos_get(path: str):
    r = requests.get(onos_url(path), auth=(ONOS['user'], ONOS['pass']), timeout=5)
    r.raise_for_status()
    return r.json()

def onos_post(path: str, payload: dict, app_id: str = DEFAULT_APP_ID):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-ONOS-Application-Id": app_id,
    }
    r = requests.post(
        onos_url(path),
        json=payload,
        auth=(ONOS['user'], ONOS['pass']),
        headers=headers,
        timeout=5,
    )
    r.raise_for_status()
    return r.json() if r.text else {"ok": True}

def onos_delete(path: str, app_id: str = DEFAULT_APP_ID):
    headers = {
        "Accept": "application/json",
        "X-ONOS-Application-Id": app_id,
    }
    r = requests.delete(
        onos_url(path),
        auth=(ONOS['user'], ONOS['pass']),
        headers=headers,
        timeout=5,
    )
    r.raise_for_status()
    return r.json() if r.text else {"ok": True}

# ------------- ONOS commands -------------
def onos_list_devices(_=None):
    js = onos_get("/onos/v1/devices")
    for d in js.get("devices", []):
        print(d["id"], d["type"], d["available"])
    print("\nTip: use 'onos-links' to see the s0a<->s0b link ports.")

def onos_list_links(_=None):
    js = onos_get("/onos/v1/links")
    for l in js.get("links", []):
        print(f"{l['src']['device']}/{l['src']['port']} <-> {l['dst']['device']}/{l['dst']['port']} ({l['state']})")

def onos_add_ptp_intent(ing_dev, ing_port, eg_dev, eg_port, src_ip, dst_ip,
                        priority=30000, app_id: str = DEFAULT_APP_ID):
    """
    Create a PointToPointIntent that matches IPv4 src/dst and steers across cores.
    NOTE: In ONOS 2.5.x, appId must be present in JSON and must correspond to an installed app.
    """
    payload = {
        "type": "PointToPointIntent",
        "appId": app_id,         # required on ONOS 2.5.x
        "priority": priority,
        "ingressPoint": {"device": ing_dev, "port": str(ing_port)},
        "egressPoint":  {"device": eg_dev, "port": str(eg_port)},
        "selector": {
            "criteria": [
                {"type": "ETH_TYPE", "ethType": "0x0800"},
                {"type": "IPV4_SRC", "ip": f"{src_ip}/32"},
                {"type": "IPV4_DST", "ip": f"{dst_ip}/32"},
            ]
        },
        # empty treatment is fine for plain IP steering
        "treatment": {}
    }
    onos_post("/onos/v1/intents", payload, app_id=app_id)
    print("[ONOS] PointToPointIntent installed")

def onos_list_intents(_=None):
    js = onos_get("/onos/v1/intents")
    for it in js.get("intents", []):
        print(it.get("key"), it.get("type"), it.get("state"))

def onos_withdraw_intent(key, app_id: str = DEFAULT_APP_ID):
    onos_delete(f"/onos/v1/intents/{key}", app_id=app_id)
    print(f"[ONOS] intent {key} withdrawn")

# ------------- Child (Ryu) helpers -------------
def load_cfg():
    with open(os.path.join(HERE, 'config.yaml'), 'r') as f:
        return yaml.safe_load(f)

def curl_child(child, path, method='GET', payload=None, timeout=2):
    base = f"http://{child['ip']}:{child['rest_port']}{path}"
    if method == 'GET':
        r = requests.get(base, timeout=timeout)
    else:
        r = requests.post(base, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()

# ------------- OVS helpers -------------
def ovs_set_controller(sw, target):
    # target example: "tcp:127.0.0.1:6653"
    cmd = ['sudo', 'ovs-vsctl', 'set-controller', sw, target]
    subprocess.check_call(cmd)

def ofctl_add_flow(sw, flow):
    # Always use OpenFlow 1.3 to match Ryu apps
    cmd = ['sudo', 'ovs-ofctl', '-O', 'OpenFlow13', 'add-flow', sw, flow]
    subprocess.check_call(cmd)

def ofctl_del_flow_strict(sw, flow):
    cmd = ['sudo', 'ovs-ofctl', '-O', 'OpenFlow13', '--strict', 'del-flows', sw, flow]
    subprocess.check_call(cmd)

# ------------- Cross-site pinning via ovs-ofctl (fallback/manual) -------------
def push_crosssite(src_ip, dst_ip):
    """
    Manually pin traffic src_ip -> dst_ip across the inter-core link (port 3).
    """
    # A->B on s0a: send towards WAN (port3)
    ofctl_add_flow('s0a', f'priority=3000,ip,nw_src={src_ip},nw_dst={dst_ip},actions=output:3')
    # A<-B on s0a (return towards site A over WAN)
    ofctl_add_flow('s0a', f'priority=3000,ip,nw_src={dst_ip},nw_dst={src_ip},actions=output:3')

    # On s0b do the symmetric pin across WAN
    ofctl_add_flow('s0b', f'priority=3000,ip,nw_src={src_ip},nw_dst={dst_ip},actions=output:3')
    ofctl_add_flow('s0b', f'priority=3000,ip,nw_src={dst_ip},nw_dst={src_ip},actions=output:3')

def clear_crosssite(src_ip, dst_ip):
    ofctl_del_flow_strict('s0a', f'priority=3000,ip,nw_src={src_ip},nw_dst={dst_ip}')
    ofctl_del_flow_strict('s0a', f'priority=3000,ip,nw_src={dst_ip},nw_dst={src_ip}')
    ofctl_del_flow_strict('s0b', f'priority=3000,ip,nw_src={src_ip},nw_dst={dst_ip}')
    ofctl_del_flow_strict('s0b', f'priority=3000,ip,nw_src={dst_ip},nw_dst={src_ip}')

# ------------- Orchestrator features -------------
def health(args):
    cfg = load_cfg()
    for name, child in cfg['children'].items():
        try:
            js = curl_child(child, '/health')
            print(f"[{name}] OK {js}")
        except Exception as e:
            print(f"[{name}] DOWN ({e})")

def push_blocklist(args):
    cfg = load_cfg()
    rule = json.loads(args.rule)
    for name, child in cfg['children'].items():
        try:
            js = curl_child(child, '/blocklist', method='POST', payload=rule)
            print(f"[{name}] applied: {js.get('applied')}")
        except Exception as e:
            print(f"[{name}] ERROR applying blocklist: {e}")

def monitor_failover(args):
    cfg = load_cfg()
    master = cfg['master']
    target_master = f"tcp:{master['ip']}:{master['of_port']}"
    backoff = 0.5
    print("[orchestrator] monitoring children for failover... Ctrl+C to stop")
    while True:
        for name, child in cfg['children'].items():
            try:
                curl_child(child, '/health', timeout=1.0)
            except Exception:
                print(f"[FAILOVER] {name} appears DOWN → rebind its switches to MASTER")
                for sw in child['switches']:
                    ovs_set_controller(sw, target_master)
        time.sleep(backoff)

def rebind(args):
    cfg = load_cfg()
    master = cfg['master']
    if args.to == 'master':
        target = f"tcp:{master['ip']}:{master['of_port']}"
    else:
        child = cfg['children'][args.to]
        target = f"tcp:{child['ip']}:{child['of_port']}"
    for sw in args.switches.split(','):
        sw = sw.strip()
        if sw:
            print(f"[rebind] {sw} -> {target}")
            ovs_set_controller(sw, target)

# ------------- CLI -------------
def main():
    ap = argparse.ArgumentParser(prog='orchestrator')
    sub = ap.add_subparsers(dest='cmd')

    s1 = sub.add_parser('health', help='check /health on children')
    s1.set_defaults(func=health)

    s2 = sub.add_parser('push-blocklist', help='push global blocklist rule (JSON string)')
    s2.add_argument('--rule', required=True, help='e.g. {"src_ip":"10.0.0.1","dst_ip":"10.0.0.5","proto":"tcp","dport":80}')
    s2.set_defaults(func=push_blocklist)

    s3 = sub.add_parser('monitor-failover', help='monitor children, rebind dead child switches to master')
    s3.set_defaults(func=monitor_failover)

    s4 = sub.add_parser('rebind', help='manually rebind switches')
    s4.add_argument('--to', required=True, choices=['master','A','B'])
    s4.add_argument('--switches', required=True, help='comma-separated names, e.g., s1a,s2a')
    s4.set_defaults(func=rebind)

    s5 = sub.add_parser('push-crosssite', help='pin A<->B traffic across WAN (cores port3)')
    s5.add_argument('--src', required=True)
    s5.add_argument('--dst', required=True)
    s5.set_defaults(func=lambda a: push_crosssite(a.src, a.dst))

    s6 = sub.add_parser('clear-crosssite', help='remove pinned A<->B WAN flows')
    s6.add_argument('--src', required=True)
    s6.add_argument('--dst', required=True)
    s6.set_defaults(func=lambda a: clear_crosssite(a.src, a.dst))

    s7 = sub.add_parser('onos-devices', help='list ONOS devices')
    s7.set_defaults(func=onos_list_devices)

    s8 = sub.add_parser('onos-links', help='list ONOS links')
    s8.set_defaults(func=onos_list_links)

    s9 = sub.add_parser('onos-add-ptp', help='add a PointToPointIntent with IPv4 selector')
    s9.add_argument('--ing-dev', required=True)
    s9.add_argument('--ing-port', required=True, type=int)
    s9.add_argument('--eg-dev', required=True)
    s9.add_argument('--eg-port', required=True, type=int)
    s9.add_argument('--src', required=True, help='IPv4 src (e.g., 10.0.0.1)')
    s9.add_argument('--dst', required=True, help='IPv4 dst (e.g., 10.0.0.5)')
    s9.set_defaults(func=lambda a: onos_add_ptp_intent(
        a.ing_dev, a.ing_port, a.eg_dev, a.eg_port, a.src, a.dst, app_id=DEFAULT_APP_ID
    ))

    s10 = sub.add_parser('onos-intents', help='list intents')
    s10.set_defaults(func=onos_list_intents)

    s11 = sub.add_parser('onos-del', help='withdraw intent by key')
    s11.add_argument('--key', required=True)
    s11.set_defaults(func=lambda a: onos_withdraw_intent(a.key, app_id=DEFAULT_APP_ID))

    args = ap.parse_args()
    if not hasattr(args, 'func'):
        ap.print_help(); sys.exit(1)
    args.func(args)

if __name__ == '__main__':
    main()
