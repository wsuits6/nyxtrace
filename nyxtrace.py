#!/usr/bin/env python3
"""
Nyxtrace - Main CLI Entry Point
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from core.banner import print_banner, VERSION
from core.config import NyxConfig
from core.engine import NyxEngine

async def main():
    parser = argparse.ArgumentParser(description="Nyxtrace DNS Recon Framework")
    parser.add_argument('-t', '--target', required=True, help="Target domain/IP")
    parser.add_argument('-o', '--output', default='output', help="Output directory")
    parser.add_argument('-w', '--wordlist', default='wordlists/default.txt')
    parser.add_argument('--threads', type=int, default=50)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()]
    )
    
    print_banner()
    console = Console()
    
    # Initialize
    config = NyxConfig.from_cli(
        target=args.target,
        output_dir=Path(args.output),
        wordlist=Path(args.wordlist),
        threads=args.threads,
        verbose=args.verbose
    )
    
    engine = NyxEngine(config)
    
    # Execute
    if await engine.load_target(args.target):
        console.print(f"[green]✓ Target loaded: {args.target}")
        results = await engine.enumerate_records()
        console.print(f"[green]✓ Scan complete. Results: {len(results)} modules")
    else:
        console.print("[red]✗ Invalid target")
        sys.exit(1)
    
    engine.close()

if __name__ == "__main__":
    asyncio.run(main())
