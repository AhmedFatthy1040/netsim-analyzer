from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import ipaddress

@dataclass
class DHCPLease:
    ip_address: str
    mac_address: str
    lease_time: int  # in seconds
    start_time: datetime
    subnet_mask: str
    gateway: str
    dns_servers: List[str]

class DHCPServer:
    def __init__(self, subnet: str, start_ip: str, end_ip: str, 
                 lease_time: int = 3600, gateway: str = None,
                 dns_servers: List[str] = None):
        self.subnet = ipaddress.ip_network(subnet)
        self.start_ip = ipaddress.ip_address(start_ip)
        self.end_ip = ipaddress.ip_address(end_ip)
        self.lease_time = lease_time
        self.gateway = gateway or str(next(self.subnet.hosts()))
        self.dns_servers = dns_servers or ["8.8.8.8", "8.8.4.4"]
        
        # Track leases: mac_address -> DHCPLease
        self.active_leases: Dict[str, DHCPLease] = {}
        # Track used IPs: ip_address -> mac_address
        self.used_ips: Dict[str, str] = {}
        
        print(f"DHCP Server initialized for subnet {subnet}")

    def discover(self, mac_address: str) -> Optional[str]:
        """Handle DHCP DISCOVER message."""
        print(f"DHCP DISCOVER from {mac_address}")
        
        # Check if client already has a lease
        if mac_address in self.active_leases:
            offered_ip = self.active_leases[mac_address].ip_address
            print(f"Found existing lease for {mac_address}: {offered_ip}")
            return offered_ip

        # Find available IP
        offered_ip = self._get_available_ip()
        if offered_ip:
            print(f"Offering IP {offered_ip} to {mac_address}")
            return str(offered_ip)
        
        print(f"No available IPs for {mac_address}")
        return None

    def request(self, mac_address: str, requested_ip: str) -> Optional[DHCPLease]:
        """Handle DHCP REQUEST message."""
        print(f"DHCP REQUEST from {mac_address} for {requested_ip}")
        
        # Validate requested IP is in our range
        ip = ipaddress.ip_address(requested_ip)
        if not (self.start_ip <= ip <= self.end_ip):
            print(f"Requested IP {requested_ip} not in range")
            return None

        # Check if IP is already leased to another client
        if requested_ip in self.used_ips and self.used_ips[requested_ip] != mac_address:
            print(f"IP {requested_ip} already leased to another client")
            return None

        # Create or update lease
        lease = DHCPLease(
            ip_address=requested_ip,
            mac_address=mac_address,
            lease_time=self.lease_time,
            start_time=datetime.now(),
            subnet_mask=str(self.subnet.netmask),
            gateway=self.gateway,
            dns_servers=self.dns_servers
        )
        
        self.active_leases[mac_address] = lease
        self.used_ips[requested_ip] = mac_address
        print(f"Lease granted for {mac_address}: {requested_ip}")
        return lease

    def release(self, mac_address: str) -> None:
        """Handle DHCP RELEASE message."""
        if mac_address in self.active_leases:
            lease = self.active_leases[mac_address]
            del self.used_ips[lease.ip_address]
            del self.active_leases[mac_address]
            print(f"Lease released for {mac_address}: {lease.ip_address}")

    def _get_available_ip(self) -> Optional[str]:
        """Find an available IP address in the pool."""
        current = self.start_ip
        while current <= self.end_ip:
            if str(current) not in self.used_ips:
                return str(current)
            current += 1
        return None

    def _cleanup_expired_leases(self) -> None:
        """Remove expired leases."""
        now = datetime.now()
        expired = []
        for mac, lease in self.active_leases.items():
            if now - lease.start_time > timedelta(seconds=lease.lease_time):
                expired.append(mac)
        
        for mac in expired:
            self.release(mac)

class DHCPClient:
    def __init__(self, mac_address: str):
        self.mac_address = mac_address
        self.current_lease: Optional[DHCPLease] = None
        print(f"DHCP Client initialized with MAC {mac_address}")

    def request_lease(self, server: DHCPServer) -> bool:
        """Attempt to get a DHCP lease."""
        # DHCP DISCOVER
        offered_ip = server.discover(self.mac_address)
        if not offered_ip:
            print(f"No IP offered to {self.mac_address}")
            return False

        # DHCP REQUEST
        lease = server.request(self.mac_address, offered_ip)
        if lease:
            self.current_lease = lease
            print(f"Lease obtained: {lease.ip_address}")
            return True
        
        print(f"Failed to obtain lease for {self.mac_address}")
        return False

    def release_lease(self, server: DHCPServer) -> None:
        """Release current DHCP lease."""
        if self.current_lease:
            server.release(self.mac_address)
            self.current_lease = None