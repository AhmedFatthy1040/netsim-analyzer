from typing import Dict, List, Optional, Union
from src.protocols.bgp import BGPRouter
from src.protocols.ospf import OSPFRouter, LSA
import networkx as nx
import matplotlib.pyplot as plt

class NetworkSimulator:
    def __init__(self):
        self.bgp_routers: Dict[str, BGPRouter] = {}
        self.ospf_routers: Dict[str, OSPFRouter] = {}
        self.topology = nx.Graph()

    def add_router(self, router_id: str, router_type: str, **kwargs) -> None:
        """Add a router to the network simulation."""
        if router_type.upper() == "BGP":
            router = BGPRouter(as_number=kwargs.get('as_number', 1), router_id=router_id)
            self.bgp_routers[router_id] = router
        elif router_type.upper() == "OSPF":
            router = OSPFRouter(router_id=router_id, area_id=kwargs.get('area_id', '0'))
            self.ospf_routers[router_id] = router
        
        self.topology.add_node(router_id, type=router_type)

    def connect_routers(self, router1_id: str, router2_id: str, cost: float = 1.0) -> None:
        """Connect two routers in the topology."""
        # Add the connection to the topology graph
        self.topology.add_edge(router1_id, router2_id, weight=cost)

        # Connect BGP peers if both are BGP routers
        if router1_id in self.bgp_routers and router2_id in self.bgp_routers:
            self.bgp_routers[router1_id].add_peer(self.bgp_routers[router2_id])
            self.bgp_routers[router2_id].add_peer(self.bgp_routers[router1_id])
        
        # Connect OSPF neighbors if both are OSPF routers
        if router1_id in self.ospf_routers and router2_id in self.ospf_routers:
            router1 = self.ospf_routers[router1_id]
            router2 = self.ospf_routers[router2_id]
            
            # Add neighbors with references to the actual router objects
            router1.add_neighbor(router2_id, cost, router2)
            router2.add_neighbor(router1_id, cost, router1)

            # Share existing LSDBs between the routers
            for lsa in router1.lsdb.values():
                router2.receive_lsa(lsa)
            for lsa in router2.lsdb.values():
                router1.receive_lsa(lsa)

            # Generate and exchange new LSAs
            lsa1 = router1._generate_lsa()
            lsa2 = router2._generate_lsa()
            
            # Each router floods its LSA to its neighbors
            router1._flood_lsa(lsa1)
            router2._flood_lsa(lsa2)

    def advertise_bgp_route(self, router_id: str, prefix: str, next_hop: str) -> None:
        """Advertise a BGP route from a specific router."""
        if router_id in self.bgp_routers:
            self.bgp_routers[router_id].advertise_route(prefix, next_hop)

    def visualize_topology(self) -> None:
        """Visualize the network topology using networkx and matplotlib."""
        pos = nx.spring_layout(self.topology)
        
        # Draw BGP routers
        bgp_nodes = [n for n in self.topology.nodes() if n in self.bgp_routers]
        nx.draw_networkx_nodes(self.topology, pos, nodelist=bgp_nodes, 
                             node_color='lightblue', node_size=500, label='BGP')
        
        # Draw OSPF routers
        ospf_nodes = [n for n in self.topology.nodes() if n in self.ospf_routers]
        nx.draw_networkx_nodes(self.topology, pos, nodelist=ospf_nodes,
                             node_color='lightgreen', node_size=500, label='OSPF')
        
        # Draw edges and labels
        nx.draw_networkx_edges(self.topology, pos)
        nx.draw_networkx_labels(self.topology, pos)
        
        plt.title("Network Topology")
        plt.legend()
        plt.axis('off')
        plt.show()

    def get_route_info(self, source: str, destination: str) -> dict:
        """Get routing information between two points in the network."""
        result = {
            'source': source,
            'destination': destination,
            'path': None,
            'protocol': None
        }

        if source in self.bgp_routers and destination in self.bgp_routers:
            # For BGP, find any route that reaches the destination AS
            source_router = self.bgp_routers[source]
            dest_router = self.bgp_routers[destination]
            # Look for any route that ends with the destination AS number
            for prefix, route in source_router.routing_table.items():
                if route.as_path and route.as_path[-1] == dest_router.as_number:
                    result.update({
                        'protocol': 'BGP',
                        'path': route.as_path,
                        'next_hop': route.next_hop
                    })
                    break
        elif source in self.ospf_routers and destination in self.ospf_routers:
            route = self.ospf_routers[source].get_route(destination)
            if route:
                result.update({
                    'protocol': 'OSPF',
                    'next_hop': route[0],
                    'cost': route[1]
                })

        return result