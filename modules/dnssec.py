"""
DNSSEC Validation and Configuration Analysis Module
"""

import dns.resolver
import dns.dnssec
from typing import Dict, List, Any
from ..core.config import NyxConfig
from ..core.target import Target
from ..core.storage import EvidenceStore

class DNSSECMODULE:
    def __init__(self, config: NyxConfig, target: Target, store: EvidenceStore):
        self.config = config
        self.target = target
        self.store = store
        self.results = {'module': 'dnssec', 'records': [], 'findings': []}
    
    async def run(self) -> Dict[str, Any]:
        """Analyze DNSSEC configuration."""
        await self._check_dnssec_records()
        await self._validate_chain()
        return self.results
    
    async def _check_dnssec_records(self):
        """Check for DNSSEC records (DNSKEY, DS, RRSIG)."""
        for rtype in ['DNSKEY', 'DS', 'RRSIG']:
            records = await self._query_record(rtype)
            self.results['records'].extend(records)
    
    async def _query_record(self, rtype: str) -> List[Dict]:
        records = []
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.config.dns_timeout
            answers = resolver.resolve(self.target.fqdn, rtype)
            
            for rdata in answers:
                records.append({
                    'type': rtype,
                    'name': str(self.target.fqdn),
                    'data': str(rdata),
                    'ttl': rdata.ttl
                })
        except:
            self._add_finding('missing_dnssec', f"No {rtype} records found")
        
        return records
    
    async def _validate_chain(self):
        """Basic DNSSEC chain validation."""
        try:
            resolver = dns.resolver.Resolver()
            resolver.use_dnssec = True
            resolver.resolve(self.target.fqdn, 'A')
        except dns.resolver.ValidationFailure:
            self._add_finding('dnssec_validation_failure', 'DNSSEC validation failed')
        except:
            self._add_finding('dnssec_not_deployed', 'No DNSSEC deployment detected')
    
    def _add_finding(self, ftype: str, message: str):
        self.results['findings'].append({
            'type': ftype,
            'severity': 'medium',
            'message': message
        })
