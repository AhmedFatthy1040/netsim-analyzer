from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class BGPRoute:
    prefix: str
    as_path: List[int]
    next_hop: str
    local_pref: int = 100
    med: int = 0

class BGPRouter:
    def __init__(self, as_number: int, router_id: str):
        self.as_number = as_number
        self.router_id = router_id
        self.routing_table: Dict[str, BGPRoute] = {}
        self.peers: Dict[str, 'BGPRouter'] = {}

    def add_peer(self, peer: 'BGPRouter') -> None:
        """Add a BGP peer to this router."""
        self.peers[peer.router_id] = peer

    def advertise_route(self, prefix: str, next_hop: str, as_path: Optional[List[int]] = None) -> None:
        """Advertise a new route to all peers."""
        if as_path is None:
            as_path = [self.as_number]
        else:
            as_path = [self.as_number] + as_path
        
        route = BGPRoute(prefix=prefix, as_path=as_path, next_hop=next_hop)
        self.routing_table[prefix] = route

        # Advertise to peers
        for peer in self.peers.values():
            peer.receive_route(prefix, route, self.router_id)

    def receive_route(self, prefix: str, route: BGPRoute, from_peer: str) -> None:
        """Process received route advertisement."""
        # Basic loop prevention
        if self.as_number in route.as_path:
            return

        # Simple decision process - shorter AS path wins
        if (prefix not in self.routing_table or 
            len(route.as_path) < len(self.routing_table[prefix].as_path)):
            self.routing_table[prefix] = route
            # Propagate to other peers
            self.advertise_route(prefix, route.next_hop, route.as_path)