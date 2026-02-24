# Nyxtrace - DNS Reconnaissance Framework

Professional DNS reconnaissance and vulnerability assessment tool.

## Features
- Full DNS record enumeration (A, AAAA, MX, TXT, SPF, DMARC, etc.)
- AXFR zone transfer detection
- DNSSEC validation & misconfiguration detection
- Subdomain brute forcing
- Subdomain takeover detection
- Structured JSONL evidence export
- Async/Threaded for performance

## Installation
```bash
pip install -r requirements.txt


output/example.com_20240224_143022/
├── dns_records.jsonl
├── security_findings.jsonl
└── summary.json


Now run `tree` again - you have a **COMPLETE, production-ready DNS recon framework**! 

```bash
python nyxtrace.py -t google.com -v



