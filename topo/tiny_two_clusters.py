#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info

def build_net():
    net = Mininet(controller=None, switch=OVSSwitch, link=TCLink, autoSetMacs=True)

    info('*** Adding controllers (placeholders, we attach per-switch below)\n')
    cA = net.addController('cA', controller=RemoteController, ip='127.0.0.1', port=6633)
    cB = net.addController('cB', controller=RemoteController, ip='127.0.0.1', port=6634)
    cM = net.addController('cM', controller=RemoteController, ip='127.0.0.1', port=6653)

    info('*** Adding switches\n')
    s0 = net.addSwitch('s0')   # core, owned by master
    s1 = net.addSwitch('s1')   # ToR-A, owned by child-A
    s2 = net.addSwitch('s2')   # ToR-B, owned by child-B

    info('*** Adding links\n')
    net.addLink(s0, s1)
    net.addLink(s0, s2)

    info('*** Adding hosts\n')
    # hA1 = net.addHost('hA1', ip='10.0.1.1/24')
    # hA2 = net.addHost('hA2', ip='10.0.1.2/24')
    # NEW (same /24 for everyone)
    hA1 = net.addHost('hA1', ip='10.0.0.1/24')
    hA2 = net.addHost('hA2', ip='10.0.0.2/24')

    net.addLink(hA1, s1)
    net.addLink(hA2, s1)

    # hB1 = net.addHost('hB1', ip='10.0.2.1/24')
    # hB2 = net.addHost('hB2', ip='10.0.2.2/24')
    hB1 = net.addHost('hB1', ip='10.0.0.3/24')
    hB2 = net.addHost('hB2', ip='10.0.0.4/24')
    net.addLink(hB1, s2)
    net.addLink(hB2, s2)

    info('*** Building network\n')
    net.build()

    info('*** Starting controllers\n')
    for c in (cA, cB, cM):
        c.start()

    info('*** Binding switches to specific controllers\n')
    s1.start([cA])   # Cluster A → Child-A
    s2.start([cB])   # Cluster B → Child-B
    s0.start([cM])   # Core → Master

    info('*** Network is up\n')
    return net

def main():
    setLogLevel('info')
    net = build_net()
    info('*** Basic connectivity test: pingall\n')
    net.pingAll()
    CLI(net)   # drop into CLI for manual tests
    net.stop()

if __name__ == '__main__':
    main()
