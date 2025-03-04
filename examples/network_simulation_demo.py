from src.network_simulator import NetworkSimulator
import time

def main():
    # Create a network simulation
    sim = NetworkSimulator()

    # Create BGP routers for different autonomous systems
    sim.add_router("AS1_R1", "BGP", as_number=1)
    sim.add_router("AS2_R1", "BGP", as_number=2)
    sim.add_router("AS3_R1", "BGP", as_number=3)

    # Create OSPF routers for internal routing
    sim.add_router("OSPF_R1", "OSPF", area_id="0")
    sim.add_router("OSPF_R2", "OSPF", area_id="0")
    sim.add_router("OSPF_R3", "OSPF", area_id="1")

    # Connect BGP routers (inter-AS connections)
    sim.connect_routers("AS1_R1", "AS2_R1", cost=1)
    sim.connect_routers("AS2_R1", "AS3_R1", cost=1)

    # Connect OSPF routers (intra-AS connections)
    sim.connect_routers("OSPF_R1", "OSPF_R2", cost=1)
    sim.connect_routers("OSPF_R2", "OSPF_R3", cost=2)

    # Advertise some BGP routes
    sim.advertise_bgp_route("AS1_R1", "192.168.1.0/24", "AS1_R1")
    sim.advertise_bgp_route("AS2_R1", "192.168.2.0/24", "AS2_R1")
    sim.advertise_bgp_route("AS3_R1", "192.168.3.0/24", "AS3_R1")

    # Let the network converge
    time.sleep(1)

    # Check routing information
    bgp_route = sim.get_route_info("AS1_R1", "AS3_R1")
    ospf_route = sim.get_route_info("OSPF_R1", "OSPF_R3")

    print("\nBGP Route Information:")
    print(f"From {bgp_route['source']} to {bgp_route['destination']}")
    print(f"Protocol: {bgp_route['protocol']}")
    print(f"Next Hop: {bgp_route.get('next_hop')}")
    if 'path' in bgp_route:
        print(f"AS Path: {bgp_route['path']}")

    print("\nOSPF Route Information:")
    print(f"From {ospf_route['source']} to {ospf_route['destination']}")
    print(f"Protocol: {ospf_route['protocol']}")
    print(f"Next Hop: {ospf_route.get('next_hop')}")
    print(f"Cost: {ospf_route.get('cost')}")

    # Visualize the network topology
    print("\nDisplaying network topology...")
    sim.visualize_topology()

if __name__ == "__main__":
    main()