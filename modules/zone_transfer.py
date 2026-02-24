"""
AXFR Zone Transfer Detection Module
Attempts zone transfers against all authoritative nameservers.
"""

import dns.query
import dns.zone
import dns.resolver
from typing import Dict, List, Any
from ..core.config import NyxConfig
from ..core.target import Target
from ..core.storage import EvidenceStore

class ZoneTransferModule:
    def __init__(self, config: NyxConfig, target: Target, store: EvidenceStore):
        self.config = config
        self.target = target
        self.store = store
        self.results = {
            'module': 'zone_transfer',
            'records': [],
            'findings': []
        }
    
    async def run(self) -> Dict[str, Any]:
        """Execute zone transfer attempts against all nameservers."""
        if not self.target.nameservers:
            self._add_finding('info', 'No nameservers discovered')
            return self.results
        
        tasks = [self._attempt_transfer(ns) for ns in self.target.nameservers]
        transfer_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in transfer_results:
            if isinstance(result, dict):
                self.results['records'].extend(result.get('records', []))
                self.results['findings'].extend(result.get('findings', []))
        
        await self.store.store_records(self.results['records'])
        for finding in self.results['findings']:
            await self.store.store_finding(finding)
            
        return self.results
    
    async def _attempt_transfer(self, nameserver: str) -> Dict[str, Any]:
        """Attempt AXFR from single nameserver."""
        records = []
        findings = []
        
        try:
            q = dns.message.make_query(self.target.fqdn, 'AXFR')
            response = dns.query.tcp(q, nameserver, timeout=self.config.dns_timeout)
            
            if response.answer:
                # Zone transfer successful!
                zone = dns.zone.from_xfr(response)
                records = [
                    {
                        'nameserver': nameserver,
                        'type': str(r.rdtype),
                        'name': str(r.name),
                        'data': str(r),
                        'ttl': r.ttl
                    }
                    for r in zone.iterate_rdatas()
                ]
                
                findings.append({
                    'type': 'zone_transfer_success',
                    'severity': 'critical',
                    'nameserver': nameserver,
                    'record_count': len(records),
                    'evidence': f'AXFR successful from {nameserver}'
                })
                
        except dns.exception.Timeout:
            findings.append({
                'type': 'zone_transfer_timeout',
                'severity': 'info',
                'nameserver': nameserver
            })
        except dns.resolver.NXDOMAIN:
            pass
        except Exception as e:
            findings.append({
                'type': 'zone_transfer_failure',
                'severity': 'info',
                'nameserver': nameserver,
                'error': str(e)
            })
        
        return {'records': records, 'findings': findings}
    
    def _add_finding(self, ftype: str, message: str):
        """Helper to add finding to results."""
        self.results['findings'].append({
            'type': ftype,
            'severity': 'info',
            'message': message
        })
