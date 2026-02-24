"""
Nyxtrace Core Engine - FIXED VERSION
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Fix imports - standalone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import NyxConfig
from core.target import Target
from core.storage import EvidenceStore

# Manual module imports (no registry needed for MVP)
from modules.records import RecordsModule
from modules.zone_transfer import ZoneTransferModule
from modules.dnssec import DNSSECMODULE
from modules.misconfig import MisconfigModule
from modules.takeover import TakeoverModule
from modules.subdomains import SubdomainsModule

MODULES = {
    'records': RecordsModule,
    'zone_transfer': ZoneTransferModule,
    'dnssec': DNSSECMODULE,
    'misconfig': MisconfigModule,
    'takeover': TakeoverModule,
    'subdomains': SubdomainsModule
}

log = logging.getLogger(__name__)

class NyxEngine:
    def __init__(self, config: NyxConfig):
        self.config = config
        self.target = None
        self.store = EvidenceStore(config.output_dir)
        self.results = {}
        self.executor = ThreadPoolExecutor(max_workers=config.max_threads)
        
    async def load_target(self, target_input: str) -> bool:
        """Normalize and validate target."""
        self.target = Target.resolve(target_input)
        if not self.target:
            log.error(f"Invalid target: {target_input}")
            return False
        
        log.info(f"Loaded target: {self.target.fqdn}")
        await self.store.initialize_target(self.target)
        return True
    
    async def enumerate_records(self) -> Dict[str, List[Any]]:
        """Run DNS enumeration."""
        if not self.target:
            raise RuntimeError("No target loaded")
        
        tasks = []
        for name, module_cls in MODULES.items():
            try:
                module = module_cls(self.config, self.target, self.store)
                tasks.append(self._execute_module(name, module))
            except Exception as e:
                log.warning(f"Skipping module {name}: {e}")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        await self.store.finalize_results(self.results)
        return self.results
    
    async def _execute_module(self, name: str, module) -> Dict[str, Any]:
        """Execute single module."""
        try:
            log.info(f"Executing: {name}")
            result = await asyncio.wait_for(module.run(), timeout=30.0)
            log.info(f"{name} completed")
            self.results[name] = result
            return result
        except asyncio.TimeoutError:
            log.warning(f"{name} timed out")
            return {"status": "timeout"}
        except Exception as e:
            log.error(f"{name} failed: {e}")
            return {"status": "error", "error": str(e)}

    def close(self):
        self.executor.shutdown(wait=True)