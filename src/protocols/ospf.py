from dataclasses import dataclass
from typing import Dict, List, Set, Optional
import networkx as nx
from datetime import datetime

@dataclass
class LSA:
    """Link State Advertisement"""
    router_id: str
    sequence_number: int
    age: int
    neighbors: Dict[str, float]  # neighbor_id -> cost
    area_id: str
    timestamp: datetime = datetime.now()

class OSPFRouter:
    def __init__(self, router_id: str, area_id: str = "0"):
        self.router_id = router_id
        self.area_id = area_id
        self.lsdb: Dict[str, LSA] = {}  # router_id -> LSA
        self.neighbors: Dict[str, float] = {}  # neighbor_id -> cost
        self.sequence_number = 0
        self.routing_table: Dict[str, tuple[str, float]] = {}  # dest -> (next_hop, cost)
        self.lsa_seen: Set[str] = set()  # Track seen LSAs
        self.neighbor_routers: Dict[str, 'OSPFRouter'] = {}  # neighbor_id -> router object for LSA forwarding
        print(f"Created OSPF router {router_id} in area {area_id}")

    def add_neighbor(self, neighbor_id: str, cost: float = 1.0, neighbor_router: Optional['OSPFRouter'] = None) -> None:
        """Add a neighboring router with associated cost."""
        self.neighbors[neighbor_id] = cost
        if neighbor_router:
            self.neighbor_routers[neighbor_id] = neighbor_router
        print(f"Router {self.router_id} added neighbor {neighbor_id} with cost {cost}")
        # Generate new LSA after topology change
        self._generate_lsa()

    def _generate_lsa(self) -> LSA:
        """Generate a new Link State Advertisement."""
        self.sequence_number += 1
        lsa = LSA(
            router_id=self.router_id,
            sequence_number=self.sequence_number,
            age=0,
            neighbors=self.neighbors.copy(),
            area_id=self.area_id
        )
        self.lsdb[self.router_id] = lsa
        print(f"Router {self.router_id} generated LSA seq {self.sequence_number}")
        return lsa

    def receive_lsa(self, lsa: LSA) -> None:
        """Process received LSA and update LSDB if necessary."""
        print(f"Router {self.router_id} received LSA from {lsa.router_id}")
        
        # Create unique LSA identifier
        lsa_id = f"{lsa.router_id}_{lsa.sequence_number}"
        if lsa_id in self.lsa_seen:
            print(f"Router {self.router_id} already seen LSA {lsa_id}")
            return
            
        self.lsa_seen.add(lsa_id)
        existing_lsa = self.lsdb.get(lsa.router_id)
        
        # Update LSDB if LSA is newer
        if (not existing_lsa or 
            lsa.sequence_number > existing_lsa.sequence_number or
            (lsa.sequence_number == existing_lsa.sequence_number and 
             lsa.age < existing_lsa.age)):
            self.lsdb[lsa.router_id] = lsa
            print(f"Router {self.router_id} updated LSDB with LSA from {lsa.router_id}")
            
            # Flood LSA to all other neighbors
            self._flood_lsa(lsa)
            
            # Recalculate routes
            self._run_spf()

    def _flood_lsa(self, lsa: LSA) -> None:
        """Flood LSA to all neighbors."""
        # Get all neighbors from our routing table
        for neighbor_id, neighbor_router in self.neighbor_routers.items():
            if neighbor_id != lsa.router_id:  # Don't send back to originator
                print(f"Router {self.router_id} flooding LSA from {lsa.router_id} to {neighbor_id}")
                neighbor_router.receive_lsa(lsa)

    def _run_spf(self) -> None:
        """Run Shortest Path First (Dijkstra's) algorithm."""
        print(f"Router {self.router_id} running SPF calculation")
        # Create a graph representation
        g = nx.Graph()
        
        # Add all links from LSDB
        for lsa in self.lsdb.values():
            for neighbor, cost in lsa.neighbors.items():
                g.add_edge(lsa.router_id, neighbor, weight=cost)
                print(f"Added link {lsa.router_id} -> {neighbor} cost {cost}")

        try:
            # Calculate shortest paths from this router to all others
            paths = nx.single_source_dijkstra_path(g, self.router_id)
            costs = nx.single_source_dijkstra_path_length(g, self.router_id)
            
            # Update routing table
            self.routing_table.clear()
            for dest, path in paths.items():
                if len(path) > 1:  # Exclude self
                    next_hop = path[1]  # First hop after self
                    self.routing_table[dest] = (next_hop, costs[dest])
                    print(f"Router {self.router_id} route to {dest}: next-hop={next_hop}, cost={costs[dest]}")
        except nx.NetworkXNoPath:
            print(f"Router {self.router_id} found no paths in topology")
            pass

    def get_route(self, destination: str) -> Optional[tuple[str, float]]: 
        """Get next hop and cost to reach destination."""
        route = self.routing_table.get(destination)
        print(f"Router {self.router_id} lookup route to {destination}: {route}")
        return route