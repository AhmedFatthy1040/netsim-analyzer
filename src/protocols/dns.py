from dataclasses import dataclass
from typing import Dict, List, Optional, Literal
from datetime import datetime, timedelta

RecordType = Literal['A', 'AAAA', 'CNAME', 'MX', 'NS', 'PTR', 'TXT']

@dataclass
class DNSRecord:
    name: str
    record_type: RecordType
    value: str
    ttl: int  # Time to live in seconds
    timestamp: datetime = datetime.now()

class DNSCache:
    def __init__(self):
        self.records: Dict[str, DNSRecord] = {}
    
    def add_record(self, record: DNSRecord) -> None:
        """Add a record to the cache."""
        key = f"{record.name}_{record.record_type}"
        self.records[key] = record
    
    def get_record(self, name: str, record_type: RecordType) -> Optional[DNSRecord]:
        """Get a record from cache if it exists and is not expired."""
        key = f"{name}_{record_type}"
        record = self.records.get(key)
        
        if not record:
            return None
            
        # Check if record has expired
        if datetime.now() - record.timestamp > timedelta(seconds=record.ttl):
            del self.records[key]
            return None
            
        return record

class DNSServer:
    def __init__(self, zone: str):
        self.zone = zone
        self.records: Dict[str, List[DNSRecord]] = {}
        self.cache = DNSCache()
        print(f"DNS Server initialized for zone {zone}")

    def add_record(self, name: str, record_type: RecordType, value: str, ttl: int = 3600) -> None:
        """Add a DNS record."""
        record = DNSRecord(name=name, record_type=record_type, value=value, ttl=ttl)
        
        if name not in self.records:
            self.records[name] = []
            
        # Remove any existing records of the same type
        self.records[name] = [r for r in self.records[name] if r.record_type != record_type]
        self.records[name].append(record)
        print(f"Added {record_type} record for {name}: {value}")

    def query(self, name: str, record_type: RecordType) -> List[DNSRecord]:
        """Perform a DNS query."""
        print(f"Query for {name} ({record_type})")
        
        # Check cache first
        cached = self.cache.get_record(name, record_type)
        if cached:
            print(f"Cache hit for {name}")
            return [cached]

        # Check if we are authoritative for this zone
        if not name.endswith(self.zone) and name != self.zone:
            print(f"Not authoritative for {name}")
            return []

        # Look up the record
        records = self.records.get(name, [])
        matching = [r for r in records if r.record_type == record_type]
        
        # Handle CNAME resolution
        if not matching and record_type != 'CNAME':
            cname_records = [r for r in records if r.record_type == 'CNAME']
            if cname_records:
                # Recursively resolve the CNAME
                canonical_name = cname_records[0].value
                print(f"Following CNAME {name} -> {canonical_name}")
                matching.extend(self.query(canonical_name, record_type))

        # Cache the results
        for record in matching:
            self.cache.add_record(record)
            
        return matching

    def reverse_query(self, ip_address: str) -> List[DNSRecord]:
        """Perform a reverse DNS lookup."""
        print(f"Reverse query for {ip_address}")
        
        # Convert IP to reverse lookup format
        parts = ip_address.split('.')
        reverse_name = f"{'.'.join(reversed(parts))}.in-addr.arpa"
        
        return self.query(reverse_name, 'PTR')

class DNSClient:
    def __init__(self):
        self.cache = DNSCache()
        self.nameservers: List[DNSServer] = []

    def add_nameserver(self, server: DNSServer) -> None:
        """Add a DNS server to query."""
        self.nameservers.append(server)

    def resolve(self, name: str, record_type: RecordType) -> List[DNSRecord]:
        """Resolve a DNS query using configured nameservers."""
        print(f"Resolving {name} ({record_type})")
        
        # Check local cache first
        cached = self.cache.get_record(name, record_type)
        if cached:
            print(f"Using cached result for {name}")
            return [cached]

        # Query each nameserver until we get an answer
        for server in self.nameservers:
            results = server.query(name, record_type)
            if results:
                # Cache the results
                for record in results:
                    self.cache.add_record(record)
                return results

        print(f"No results found for {name}")
        return []

    def reverse_lookup(self, ip_address: str) -> List[DNSRecord]:
        """Perform a reverse DNS lookup."""
        print(f"Reverse lookup for {ip_address}")
        
        for server in self.nameservers:
            results = server.reverse_query(ip_address)
            if results:
                return results

        return []