# NetSim Analyzer

A Python-based network simulation tool for analyzing BGP, OSPF, DHCP, DNS, and other routing protocols. This project provides a practical implementation of network protocols and routing algorithms for educational and testing purposes.

## Features

- BGP (Border Gateway Protocol) simulation
  - Route advertisement and propagation
  - AS path-based route selection
  - Inter-AS connectivity
  - Loop prevention
- OSPF (Open Shortest Path First) implementation
  - Area-based routing
  - Cost-based path selection
  - Internal router communication
- DHCP and DNS protocol support
- Network topology visualization
- Flexible router configuration
- Route analysis and monitoring

## Installation

```bash
pip install -r requirements.txt
```

## Dependencies

- Python 3.8+
- networkx >= 2.8.0 - For network topology management
- scapy >= 2.5.0 - For packet manipulation and network protocol implementations
- PyYAML >= 6.0 - For configuration handling
- click >= 8.0.0 - For command line interface
- pytest >= 7.0.0 - For running tests

## Usage

Here's a basic example of creating a network simulation with BGP and OSPF routers:

```python
from src.network_simulator import NetworkSimulator

# Create a network simulation
sim = NetworkSimulator()

# Add BGP routers
sim.add_router("AS1_R1", "BGP", as_number=1)
sim.add_router("AS2_R1", "BGP", as_number=2)

# Add OSPF routers
sim.add_router("OSPF_R1", "OSPF", area_id="0")
sim.add_router("OSPF_R2", "OSPF", area_id="0")

# Connect routers
sim.connect_routers("AS1_R1", "AS2_R1", cost=1)
sim.connect_routers("OSPF_R1", "OSPF_R2", cost=1)

# Advertise routes
sim.advertise_bgp_route("AS1_R1", "192.168.1.0/24", "AS1_R1")
```

For more detailed examples, check out the `examples/` directory:
- `network_simulation_demo.py`: Demonstrates BGP and OSPF routing
- `dhcp_dns_demo.py`: Shows DHCP and DNS functionality

## Development

To contribute to the project:

1. Fork the repository
2. Create a virtual environment and install dependencies
3. Run tests using pytest
4. Submit a pull request with your changes

## License

[Add your license information here]
