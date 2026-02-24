"""
Target normalization and resolution utilities.
Supports domain → IP resolution and IP → PTR enumeration.
"""

import socket
import dns.resolver
import dns.reversename
from typing import Optional, NamedTuple
from .config import NyxConfig

class TargetType:
    DOMAIN = "domain"
    IP = "ip"
    CNAME = "cname"

class Target(NamedTuple):
    fqdn: str
    resolved_ips: list[str]
    type: str
    nameservers: list[str] = []
    
    @classmethod
    def resolve(cls, input_str: str) -> Optional['Target']:
        """Normalize target input to structured Target object."""
        input_str = input_str.strip().lower().rstrip('.')
        
        # Check if IP address
        try:
            socket.inet_pton(socket.AF_INET, input_str)
            return cls(fqdn=input_str, resolved_ips=[input_str], type=TargetType.IP)
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, input_str)
                return cls(fqdn=input_str, resolved_ips=[input_str], type=TargetType.IP)
            except socket.error:
                pass
        
        # Domain - resolve A/AAAA records
        ips = cls._resolve_ips(input_str)
        ns = cls._resolve_nameservers(input_str)
        
        return cls(fqdn=input_str, resolved_ips=ips, type=TargetType.DOMAIN, nameservers=ns)
    
    @staticmethod
    def _resolve_ips(domain: str) -> list[str]:
        """Resolve A and AAAA records."""
        ips = set()
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            for rdtype in ['A', 'AAAA']:
                try:
                    answers = resolver.resolve(domain, rdtype)
                    ips.update(str(r.address) for r in answers)
                except Exception:
                    continue
        except Exception:
            pass
        return sorted(ips)
    
    @staticmethod
    def _resolve_nameservers(domain: str) -> list[str]:
        """Resolve authoritative nameservers."""
        try:
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(domain, 'NS')
            return sorted(str(r.target).rstrip('.') for r in answers)
        except:
            return []
