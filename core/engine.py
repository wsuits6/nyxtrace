"""
Nyxtrace Core Engine - DNS Reconnaissance Framework
Handles target normalization, module orchestration, and result aggregation.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from .config import NyxConfig
from .target import Target
from .storage import EvidenceStore
from ..modules import MODULE_REGISTRY

log = logging.getLogger(__name__)

class NyxEngine:
    def __init__(self, config: NyxConfig):
        self.config = config
        self.target = None
        self.store = EvidenceStore(config.output_dir)
        self.results = {}
        self.executor = ThreadPoolExecutor(max_workers=config.max_threads)
        
    async def load_target(self, target_input: str) -> bool:
        """Normalize and validate target (domain/IP)."""
        self.target = Target.resolve(target_input)
        if not self.target:
            log.error(f"Invalid target: {target_input}")
            return False
        
        log.info(f"Loaded target: {self.target.fqdn} ({self.target.type})")
        await self.store.initialize_target(self.target)
        return True
    
    async def enumerate_records(self) -> Dict[str, List[Any]]:
        """Run comprehensive DNS record enumeration across all modules."""
        if not self.target:
            raise RuntimeError("No target loaded")
        
        tasks = []
        for module_name, module_cls in MODULE_REGISTRY.items():
            module = module_cls(self.config, self.target, self.store)
            tasks.append(self._execute_module(module_name, module))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        self.results = dict(zip(MODULE_REGISTRY.keys(), results))
        
        await self.store.finalize_results(self.results)
        return self.results
    
    async def _execute_module(self, name: str, module) -> Dict[str, Any]:
        """Execute single module with timeout and error handling."""
        try:
            log.info(f"Executing module: {name}")
            result = await asyncio.wait_for(module.run(), timeout=self.config.module_timeout)
            log.info(f"Module {name} completed: {len(result.get('records', []))} records")
            return {name: result}
        except asyncio.TimeoutError:
            log.warning(f"Module {name} timed out")
            return {name: {"status": "timeout", "error": "Module execution exceeded timeout"}}
        except Exception as e:
            log.error(f"Module {name} failed: {e}")
            return {name: {"status": "error", "error": str(e)}}

    def close(self):
        self.executor.shutdown(wait=True)
