from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.node import Host, OVSKernelSwitch, RemoteController

from random import randint
import http.client as http
import json

REMOTE_IP = '192.168.64.1'
BROADCAST_MAC = 'ff:ff:ff:ff:ff:ff:ff:ff'

c0 = RemoteController('c0', ip=REMOTE_IP, port=6653)

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
        self.addLink(host1, switch1, 1, 1, bw=BAND_WIDTH, cls=TCLink, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host2, switch2, 2, 2, bw=BAND_WIDTH, cls=TCLink, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host3, switch3, 3, 3, bw=BAND_WIDTH, cls=TCLink, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host4, switch4, 4, 4, bw=BAND_WIDTH, cls=TCLink, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host5, switch5, 5, 5, bw=BAND_WIDTH, cls=TCLink, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host6, switch6, 6, 6, bw=BAND_WIDTH, cls=TCLink, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host7, switch7, 7, 7, bw=BAND_WIDTH, cls=TCLink, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(host8, switch8, 8, 8, bw=BAND_WIDTH, cls=TCLink, delay=f'{randint(1, DELAY_MAX)}ms')

        #Add switches links
        self.addLink(switch1, switch3, 3, 1, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch1, switch8, 8, 1, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch2, switch4, 4, 2, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch2, switch5, 5, 2, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch2, switch7, 7, 2, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch3, switch4, 4, 3, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch3, switch6, 6, 3, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch3, switch8, 8, 3, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch4, switch5, 5, 4, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch4, switch7, 7, 4, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch5, switch6, 6, 5, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch5, switch7, 7, 5, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch6, switch8, 8, 6, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')
        self.addLink(switch7, switch8, 8, 7, cls=TCLink, bw=BAND_WIDTH, delay=f'{randint(1, DELAY_MAX)}ms')


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


class StaticEntryPusher:

    def __init__(self):
        pass

    def get(self):
        ret = self.rest_call({}, 'GET')
        return json.loads(ret[2])

    def set(self, data):
        ret = self.rest_call(data, 'POST')
        return ret[0] == 200

    def remove(self, objtype, data):
        ret = self.rest_call(data, 'DELETE')
        return ret[0] == 200

    def rest_call(self, data, action):
        path = '/wm/staticentrypusher/json'
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        }
        body = json.dumps(data)
        conn = http.HTTPConnection(REMOTE_IP, 8080)
        conn.request(action, path, body, headers)
        response = conn.getresponse()
        ret = (response.status, response.reason, response.read())
        conn.close()
        return ret


flow_template = {
    "switch": None,
    "name": None,
    "active": "true",
    "entry_type": "flow",
    "eth_dst": None,
    "actions": None #"output=flood"
}


def dump_flows(network):
    pusher = StaticEntryPusher()

    for i in range(1, len(network.hosts) + 1):
        switch = network.getNodeByName('s' + str(i))
        host = network.getNodeByName('h' + str(i))

        dist, parents = dijkstra(network, switch)
        for s in parents:
            if 's' in s and s != switch.name:
                ft = flow_template.copy()
                other_switch = network.getNodeByName(s)
                #Rule for other switches to this switch
                ft['switch'] = other_switch.MAC()
                ft['name'] = f'flow_{other_switch.name}_{switch.name}'
                ft['eth_dst'] = switch.MAC()
                parent_num = parents[s].replace('s', '')
                ft['actions'] = f'output={parent_num}'
                pusher.set(ft)

                #Rule for other switches to switch's host
                ft['name'] = f'flow_{other_switch.name}_{host.name}'
                ft['eth_dst'] = host.MAC()
                pusher.set(ft)

        #Rule for switch to host
        ft = flow_template.copy()
        ft['switch'] = switch.MAC()
        ft['name'] = f'flow_{switch.name}_{host.name}'
        ft['eth_dst'] = host.MAC()
        ft['actions'] = f'output={i}'
        pusher.set(ft)
        
        #Rule for broadcast
        ft = flow_template.copy()
        ft['switch'] = switch.MAC()
        ft['name'] = f'flow_{switch.name}_broad'
        ft['eth_dst'] = BROADCAST_MAC
        ft['actions'] = f'output=flood'
        pusher.set(ft)


def main():
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

    dump_flows(net)
    #Build the network and start it
    net.start()

    #Start CLI
    CLI( net )

    #Stop the network and exit
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()

topos = {'mytopo': (lambda: MyTopo())}
