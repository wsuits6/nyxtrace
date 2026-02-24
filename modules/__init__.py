"""
Module Registry - Auto-discovers all modules
"""

from importlib import import_module
from pathlib import Path
import sys

MODULE_REGISTRY = {}

# Auto-discover modules
module_dir = Path(__file__).parent
for module_file in module_dir.glob("*.py"):
    if module_file.stem not in ['__init__']:
        try:
            module_name = module_file.stem
            module = import_module(f"nyxtrace.modules.{module_name}")
            
            # Look for class with 'run' method
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (hasattr(attr, 'run') and 
                    callable(getattr(attr, 'run')) and 
                    hasattr(attr, '__init__')):
                    MODULE_REGISTRY[module_name] = attr
                    break
        except Exception as e:
            print(f"Failed to load module {module_file.stem}: {e}", file=sys.stderr)

# Manual registration for critical modules
try:
    from .records import RecordsModule
    MODULE_REGISTRY['records'] = RecordsModule
except:
    pass

try:
    from .zone_transfer import ZoneTransferModule  
    MODULE_REGISTRY['zone_transfer'] = ZoneTransferModule
except:
    pass
