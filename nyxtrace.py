#!/usr/bin/env python3
"""
Nyxtrace - Main CLI Entry Point
"""
import os
import sys
import asyncio
import argparse
import logging

# Fix imports - add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.banner import print_banner
from core.config import NyxConfig
from core.engine import NyxEngine

# Test imports
print("Loading modules...", file=sys.stderr)

async def main():
    parser = argparse.ArgumentParser(description="Nyxtrace DNS Recon Framework")
    parser.add_argument('-t', '--target', required=True, help="Target domain/IP")
    parser.add_argument('-o', '--output', default='output', help="Output directory")
    parser.add_argument('-w', '--wordlist', default='wordlists/default.txt')
    parser.add_argument('--threads', type=int, default=20, dest='threads')
    parser.add_argument('--max-threads', type=int, default=50)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    
    # Logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
        handlers=[logging.StreamHandler()]
    )
    
    print_banner()
    
    config = NyxConfig(
        target=args.target,
        output_dir=args.output,
        wordlist=args.wordlist,
        threads=args.threads,
        max_threads=args.max_threads,
        verbose=args.verbose
    )
    
    engine = NyxEngine(config)
    
    if await engine.load_target(args.target):
        print(f"[+] Target loaded: {args.target}")
        results = await engine.enumerate_records()
        print(f"[+] Scan complete: {len(results)} modules executed")
        print(f"[+] Results saved: {config.output_dir}")
    else:
        print("[-] Invalid target")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())