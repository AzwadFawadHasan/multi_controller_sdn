#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info

def build_net():
    net = Mininet(controller=None, switch=OVSSwitch, link=TCLink, autoSetMacs=True)

    # Controllers (placeholders; switches bind explicitly below)
    cA = net.addController('cA', controller=RemoteController, ip='127.0.0.1', port=6633)  # Child-A
    cB = net.addController('cB', controller=RemoteController, ip='127.0.0.1', port=6634)  # Child-B
    cM = net.addController('cM', controller=RemoteController, ip='127.0.0.1', port=6653)  # Master

    info('*** Switches (two sites)\n')
    # Site A
    s0a = net.addSwitch('s0a')  # core A (master)
    s1a = net.addSwitch('s1a')  # ToR-A1 (child-A)
    s2a = net.addSwitch('s2a')  # ToR-A2 (child-A)
    # Site B
    s0b = net.addSwitch('s0b')  # core B (master)
    s1b = net.addSwitch('s1b')  # ToR-B1 (child-B)
    s2b = net.addSwitch('s2b')  # ToR-B2 (child-B)

    info('*** Links\n')
    # Intra-site
    net.addLink(s0a, s1a); net.addLink(s0a, s2a)
    net.addLink(s0b, s1b); net.addLink(s0b, s2b)
    # Inter-site WAN
    net.addLink(s0a, s0b)  # later you can add tc params (delay/jitter)

    info('*** Hosts (single /24 for simplicity)\n')
    # Site A hosts
    hA1 = net.addHost('hA1', ip='10.0.0.1/24'); net.addLink(hA1, s1a)
    hA2 = net.addHost('hA2', ip='10.0.0.2/24'); net.addLink(hA2, s1a)
    hA3 = net.addHost('hA3', ip='10.0.0.3/24'); net.addLink(hA3, s2a)
    hA4 = net.addHost('hA4', ip='10.0.0.4/24'); net.addLink(hA4, s2a)
    # Site B hosts
    hB1 = net.addHost('hB1', ip='10.0.0.5/24'); net.addLink(hB1, s1b)
    hB2 = net.addHost('hB2', ip='10.0.0.6/24'); net.addLink(hB2, s1b)
    hB3 = net.addHost('hB3', ip='10.0.0.7/24'); net.addLink(hB3, s2b)
    hB4 = net.addHost('hB4', ip='10.0.0.8/24'); net.addLink(hB4, s2b)

    net.build()

    info('*** Start controllers\n')
    for c in (cA, cB, cM):
        c.start()

    info('*** Bind switches to controllers\n')
    # Master owns cores
    s0a.start([cM]); s0b.start([cM])
    # Children own ToRs in their site
    s1a.start([cA]); s2a.start([cA])
    s1b.start([cB]); s2b.start([cB])

    info('*** Network up\n')
    return net

def main():
    setLogLevel('info')
    net = build_net()
    info('*** Basic ping (first run may learn/ARP)\n')
    net.pingAll()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()
