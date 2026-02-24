"""
Nyxtrace ASCII Banner and Version Information
"""

BANNER = """
   ____  ____  _____    _    _  _____ _____  _____ ____  
  |  _ \\|  _ \\|_   _|  | |  | |/ ____|  __ \\|  __ \\___ \\ 
  | |_) | |_) | | |    | |__| | |    | |__) | |__) |__) |
  |  _ <|  _ <  | |    |  __  | |    |  _  /|  _  /|__ < 
  | |_) | |_) |_| |_   | |  | | |____| | \\ \\| | \\ \\__) |
  |____/|____/|_____|  |_|  |_|\\_____|_|  \\_\\_|  \\_\\____/ 
                                                        
              Advanced DNS Reconnaissance Framework
"""

VERSION = "1.0.0"
AUTHOR = "Nyxtrace Team"
DESCRIPTION = "Professional DNS reconnaissance and vulnerability assessment framework"

def print_banner():
    """Print framework banner."""
    print(BANNER)
    print(f"Version: {VERSION} | Author: {AUTHOR}")
    print(f"Usage: python nyxtrace.py -t example.com\n")

