from src.protocols.dhcp import DHCPServer, DHCPClient
from src.protocols.dns import DNSServer, DNSClient
import time

def main():
    # Initialize DHCP Server
    dhcp_server = DHCPServer(
        subnet="192.168.1.0/24",
        start_ip="192.168.1.100",
        end_ip="192.168.1.200",
        lease_time=3600,
        gateway="192.168.1.1",
        dns_servers=["192.168.1.10"]
    )

    # Initialize DNS Servers
    root_dns = DNSServer(".")
    com_dns = DNSServer(".com")
    example_dns = DNSServer("example.com")

    # Configure DNS records
    root_dns.add_record(".com", "NS", "com_dns.root")
    com_dns.add_record("example.com", "NS", "ns1.example.com")
    example_dns.add_record("www.example.com", "A", "192.168.1.50")
    example_dns.add_record("mail.example.com", "A", "192.168.1.51")
    example_dns.add_record("mail.example.com", "MX", "10 mail.example.com")
    example_dns.add_record("www2.example.com", "CNAME", "www.example.com")

    # Create DHCP clients
    client1 = DHCPClient("00:11:22:33:44:55")
    client2 = DHCPClient("AA:BB:CC:DD:EE:FF")

    # DHCP lease requests
    print("\n=== DHCP Lease Acquisition ===")
    client1.request_lease(dhcp_server)
    client2.request_lease(dhcp_server)

    # Create DNS client and configure nameservers
    dns_client = DNSClient()
    dns_client.add_nameserver(root_dns)
    dns_client.add_nameserver(com_dns)
    dns_client.add_nameserver(example_dns)

    # Perform DNS queries
    print("\n=== DNS Resolution ===")
    queries = [
        ("www.example.com", "A"),
        ("www2.example.com", "A"),  # Should follow CNAME
        ("mail.example.com", "MX"),
        ("mail.example.com", "A"),
    ]

    for name, record_type in queries:
        print(f"\nResolving {name} ({record_type})...")
        results = dns_client.resolve(name, record_type)
        for record in results:
            print(f"Result: {record.name} -> {record.value} (TTL: {record.ttl}s)")

    # Release DHCP leases
    print("\n=== DHCP Lease Release ===")
    client1.release_lease(dhcp_server)
    client2.release_lease(dhcp_server)

if __name__ == "__main__":
    main()