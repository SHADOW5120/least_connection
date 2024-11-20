from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI

class LeastConnTopo(Topo):
    def build(self):
        # Tạo các switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Tạo các host
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        # Kết nối các host với switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s3)

        # Kết nối các switch với nhau
        self.addLink(s1, s2)
        self.addLink(s2, s3)

# Tạo và chạy mạng Mininet
topo = LeastConnTopo()
net = Mininet(topo=topo, controller=Controller, switch=OVSSwitch)
net.start()

# Mở CLI Mininet
CLI(net)

# Dừng mạng khi hoàn tất
net.stop()
