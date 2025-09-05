#!/usr/bin/env python3
import argparse, time, subprocess, sys, json, requests, yaml, os

HERE = os.path.dirname(os.path.abspath(__file__))

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

def ovs_set_controller(sw, target):
    # target: "tcp:IP:PORT"
    cmd = ['ovs-vsctl', 'set-controller', sw, target]
    subprocess.check_call(cmd)

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
            # still proceed to others

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
                # healthy? if this child's switches currently point to master, return them
                # (we keep it simple; you could query ovs-vsctl get-controller to decide)
            except Exception:
                print(f"[FAILOVER] {name} appears DOWN → rebind its switches to MASTER")
                for sw in child['switches']:
                    ovs_set_controller(sw, target_master)
        time.sleep(backoff)

def rebind(args):
    cfg = load_cfg()
    master = cfg['master']
    target = None
    if args.to == 'master':
        target = f"tcp:{master['ip']}:{master['of_port']}"
    else:
        # args.to is child key: A or B
        child = cfg['children'][args.to]
        target = f"tcp:{child['ip']}:{child['of_port']}"
    for sw in args.switches.split(','):
        sw = sw.strip()
        if sw:
            print(f"[rebind] {sw} -> {target}")
            ovs_set_controller(sw, target)

def main():
    ap = argparse.ArgumentParser(prog='orchestrator')
    sub = ap.add_subparsers(dest='cmd')

    s1 = sub.add_parser('health', help='check /health on children')
    s1.set_defaults(func=health)

    s2 = sub.add_parser('push-blocklist', help='push global blocklist rule (JSON string)')
    s2.add_argument('--rule', required=True, help='JSON rule, e.g. {"src_ip":"10.0.1.1","dst_ip":"10.0.2.1","proto":"tcp","dport":80}')
    s2.set_defaults(func=push_blocklist)

    s3 = sub.add_parser('monitor-failover', help='monitor children, rebind dead child switches to master')
    s3.set_defaults(func=monitor_failover)

    s4 = sub.add_parser('rebind', help='manually rebind switches')
    s4.add_argument('--to', required=True, choices=['master','A','B'])
    s4.add_argument('--switches', required=True, help='comma-separated switch names, e.g., s1 or s1,s2')
    s4.set_defaults(func=rebind)

    args = ap.parse_args()
    if not hasattr(args, 'func'):
        ap.print_help(); sys.exit(1)
    args.func(args)

if __name__ == '__main__':
    main()
