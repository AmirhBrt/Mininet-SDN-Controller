from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.node import Host, OVSKernelSwitch, RemoteController

from random import randint


c0 = RemoteController('c0', ip='192.168.64.1', port=6653)

class MySwitch(OVSKernelSwitch):

    def start(self, controllers):
        return OVSKernelSwitch.start(self, [c0])

class MyTopo(Topo):

    def build(self):
        DELAY_MAX = 10
        BAND_WIDTH = 1000

        #Create hosts
        host1 = self.addHost('h1', cls=Host)
        host2 = self.addHost('h2', cls=Host)
        host3 = self.addHost('h3', cls=Host)
        host4 = self.addHost('h4', cls=Host)
        host5 = self.addHost('h5', cls=Host)
        host6 = self.addHost('h6', cls=Host)
        host7 = self.addHost('h7', cls=Host)
        host8 = self.addHost('h8', cls=Host)

        #Create Switches
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        switch3 = self.addSwitch('s3')
        switch4 = self.addSwitch('s4')
        switch5 = self.addSwitch('s5')
        switch6 = self.addSwitch('s6')
        switch7 = self.addSwitch('s7')
        switch8 = self.addSwitch('s8')


        #Add host to switch links
        self.addLink(host1, switch1, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host2, switch2, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host3, switch3, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host4, switch4, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host5, switch5, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host6, switch6, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host7, switch7, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host8, switch8, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')

        #Add switches links
        self.addLink(switch1, switch3, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch1, switch8, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch2, switch4, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch2, switch5, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch2, switch7, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch3, switch4, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch3, switch6, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch3, switch8, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch4, switch5, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch4, switch7, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch5, switch6, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch5, switch7, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch6, switch8, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch7, switch8, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')


def get_path_to_src(node, parents):
    if parents[node] == -1:
        return f'{node} '
    return get_path_to_src(parents[node], parents) + f'{node} '
 

def dijkstra(network, src_node):
    all_nodes = network.hosts + network.switches
    # Initialize dist to MAX and parent to None
    dist = {}
    parent = {}
    added = {}
    for i in all_nodes:
        dist[i.name] = float('inf')
        added[i.name] = False

    dist[src_node.name] = 0
    parent[src_node.name] = -1
    
    #main loop
    for i in range(len(all_nodes)):
        #Find Node with the shortest path from src

        nearest_node = None
        shortest_path = float('inf')

        for node in all_nodes:
            name = node.name
            if not added[name] and dist[name] < shortest_path:
                nearest_node = node
                shortest_path = dist[name]

        #Mark node
        added[nearest_node.name] = True
        #Update distance
        for node in all_nodes:
            links = network.linksBetween(nearest_node, node)
            if links:
                link = links[0]
                delay = int(link.intf1.params['delay'].replace('ms', ''))

                if shortest_path + delay < dist[node.name]:
                    dist[node.name] = shortest_path + delay
                    parent[node.name] = nearest_node.name

    return dist, parent

def emptyNet():

    "Create an empty network and add nodes to it."
    topo = MyTopo()

    net = Mininet(topo=topo, switch=MySwitch, build=False)
    #Adding Remote Controller
    net.addController(c0)

    #Build Network with given topology
    net.build()

    #Find route with least delay

    src = input('Enter source node name: ')
    dst = input('Enter destination node name: ')

    src_node = net.getNodeByName(src)

    dist_from_src, parents = dijkstra(net, src_node)
    print(f'Distance {src} from {dst} is \"{dist_from_src[dst]}ms\" using path: {get_path_to_src(dst, parents)}')

    #Build the network and start it
    net.start()

    #Start CLI
    CLI( net )

    #Stop the network and exit
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    emptyNet()

topos = {'mytopo': (lambda: MyTopo())}
