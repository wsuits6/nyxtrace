"""
Structured Subdomain Enumeration Module
"""

from pathlib import Path
import asyncio
from typing import Dict, List, Any
from core.config import NyxConfig
from core.target import Target
from core.storage import EvidenceStore

class SubdomainsModule:
    def __init__(self, config: NyxConfig, target: Target, store: EvidenceStore):
        self.config = config
        self.target = target
        self.store = store
        self.results = {'module': 'subdomains', 'records': [], 'findings': []}
    
    async def run(self) -> Dict[str, Any]:
        """Brute force subdomains from wordlist."""
        if not self.config.wordlist.exists():
            self._add_finding('no_wordlist', 'Wordlist not found')
            return self.results
        
        async with asyncio.throttle(rate_limit_s=self.config.rate_limit) as throttler:
            tasks = []
            with open(self.config.wordlist) as f:
                for line in f.read().splitlines()[:1000]:  # Limit for demo
                    subdomain = f"{line.strip()}.{self.target.fqdn}"
                    tasks.append(throttler.spawn(self._check_subdomain(subdomain)))
            
            results = await asyncio.gather(*tasks)
            valid_subs = [r for r in results if r['valid']]
            self.results['records'] = valid_subs
            
        return self.results
    
    async def _check_subdomain(self, subdomain: str) -> Dict:
        """Check single subdomain."""
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 2
            answer = resolver.resolve(subdomain, 'A')
            return {
                'subdomain': subdomain,
                'ips': [str(ip) for ip in answer],
                'valid': True
            }
        except:
            return {'subdomain': subdomain, 'valid': False}
