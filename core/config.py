"""
Nyxtrace Configuration Management
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List
import yaml

@dataclass
class NyxConfig:
    """Nyxtrace configuration."""
    target: str = ""
    output_dir: Path = Path("output")
    wordlist: Path = Path("wordlists/default.txt")
    threads: int = 50
    max_threads: int = 100
    dns_timeout: float = 5.0
    module_timeout: float = 30.0
    rate_limit: float = 0.1
    stealth: bool = False
    verbose: bool = False
    json_output: bool = False
    
    @classmethod
    def from_cli(cls, **kwargs):
        """Create config from CLI arguments."""
        config = cls()
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    def save(self, path: Path):
        """Save config to YAML."""
        data = {k: v for k, v in self.__dict__.items() 
                if not k.startswith('_')}
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

