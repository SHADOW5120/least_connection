from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink

class ComplexLoadBalancingTopo(Topo):
    def build(self):
        # Define switches
        s1 = self.addSwitch('s1', dpid="0000000000000001")
        s2 = self.addSwitch('s2', dpid="0000000000000002")
        s3 = self.addSwitch('s3', dpid="0000000000000003")
        s4 = self.addSwitch('s4', dpid="0000000000000004")
        s5 = self.addSwitch('s5', dpid="0000000000000005")
        s6 = self.addSwitch('s6', dpid="0000000000000006")

        # Define hosts
        h1 = self.addHost('h1', ip="10.0.0.1")
        h2 = self.addHost('h2', ip="10.0.0.2")
        h3 = self.addHost('h3', ip="10.0.0.3")
        h4 = self.addHost('h4', ip="10.0.0.4")
        h5 = self.addHost('h5', ip="10.0.0.5")
        h6 = self.addHost('h6', ip="10.0.0.6")

        # Connect hosts to switches
        self.addLink(h1, s1, port1=1, port2=1)
        self.addLink(h2, s3, port1=1, port2=1)
        self.addLink(h3, s4, port1=1, port2=1)
        self.addLink(h4, s6, port1=1, port2=1)
        self.addLink(h5, s5, port1=1, port2=1)
        self.addLink(h6, s5, port1=2, port2=2)

        # Connect switches (with multiple links for load balancing)
        self.addLink(s1, s2, port1=2, port2=1)
        self.addLink(s2, s4, port1=3, port2=2)
        self.addLink(s3, s5, port1=2, port2=3)
        self.addLink(s5, s6, port1=3, port2=4)
        self.addLink(s6, s4, port1=3, port2=4)
        self.addLink(s1, s3, port1=3, port2=3)
        self.addLink(s2, s3, port1=4, port2=4)

if __name__ == '__main__':
    topo = ComplexLoadBalancingTopo()
    net = Mininet(topo=topo, controller=Controller)
    net.start()
    CLI(net)
    net.stop()
