"""
Comprehensive DNS Record Enumeration Module
Enumerates all standard DNS record types.
"""

import dns.resolver
import dns.rdatatype
from typing import Dict, List, Any
from ..core.config import NyxConfig
from ..core.target import Target
from ..core.storage import EvidenceStore

class RecordsModule:
    RECORD_TYPES = [
        'A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA',
        'PTR', 'SRV', 'CAA', 'DMARC', 'SPF', 'TLSA'
    ]
    
    def __init__(self, config: NyxConfig, target: Target, store: EvidenceStore):
        self.config = config
        self.target = target
        self.store = store
        self.results = {'module': 'records', 'records': [], 'findings': []}
    
    async def run(self) -> Dict[str, Any]:
        """Enumerate all DNS record types."""
        tasks = [self._query_record(rtype) for rtype in self.RECORD_TYPES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                self.results['records'].extend(result)
        
        await self.store.store_records(self.results['records'])
        return self.results
    
    async def _query_record(self, rtype: str) -> List[Dict]:
        """Query single record type."""
        records = []
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.config.dns_timeout
            answers = resolver.resolve(self.target.fqdn, rtype)
            
            for rdata in answers:
                record = {
                    'type': rtype,
                    'name': str(self.target.fqdn),
                    'data': str(rdata),
                    'ttl': rdata.ttl
                }
                records.append(record)
                
        except Exception:
            pass
        
        return records
