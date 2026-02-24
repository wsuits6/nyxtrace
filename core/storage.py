"""
Structured evidence storage with JSONL, screenshots, and HAR export.
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class EvidenceStore:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.target_dir = None
        
    async def initialize_target(self, target):
        """Create structured output directory for target."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.target_dir = self.base_dir / f"{target.fqdn}_{timestamp}"
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize JSONL files
        self.records_file = self.target_dir / "dns_records.jsonl"
        self.findings_file = self.target_dir / "security_findings.jsonl"
        
    async def store_records(self, records: List[Dict]):
        """Append DNS records to JSONL with deduplication."""
        deduped = []
        if self.records_file.exists():
            with open(self.records_file, 'r') as f:
                existing = {json.dumps(r, sort_keys=True): r for r in map(json.loads, f)}
        else:
            existing = {}
        
        for record in records:
            key = json.dumps(record, sort_keys=True)
            if key not in existing:
                deduped.append(record)
                existing[key] = record
        
        if deduped:
            with open(self.records_file, 'a') as f:
                for record in deduped:
                    f.write(json.dumps(record) + '\n')
    
    async def store_finding(self, finding: Dict):
        """Store security finding with severity and evidence."""
        finding['timestamp'] = datetime.utcnow().isoformat()
        finding['target'] = str(self.target_dir.name)
        
        with open(self.findings_file, 'a') as f:
            f.write(json.dumps(finding) + '\n')
    
    async def finalize_results(self, results: Dict):
        """Generate summary report."""
        summary = {
            'target': str(self.target_dir.name),
            'timestamp': datetime.utcnow().isoformat(),
            'modules_executed': len(results),
            'total_records': 0,
            'critical_findings': 0
        }
        
        # Count records and critical findings
        for module_results in results.values():
            if isinstance(module_results, dict) and 'records' in module_results:
                summary['total_records'] += len(module_results['records'])
            if isinstance(module_results, dict) and 'findings' in module_results:
                summary['critical_findings'] += len([f for f in module_results['findings'] 
                                                   if f.get('severity') == 'critical'])
        
        summary_path = self.target_dir / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
