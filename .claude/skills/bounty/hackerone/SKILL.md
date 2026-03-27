---
name: hackerone
description: HackerOne bug bounty automation - parses scope CSVs, deploys parallel pentesting agents for each asset, auto-downloads mobile apps from running emulators, validates PoCs, and generates platform-ready submission reports. Use when testing HackerOne programs or preparing professional vulnerability submissions.
---

# HackerOne Bug Bounty Hunting

Automates HackerOne workflows: scope parsing → mobile app acquisition → parallel testing → PoC validation → submission reports.

## Quick Start

```
1. Input: HackerOne program URL or CSV file
2. Parse scope and program guidelines
3. For mobile assets: use /mobile-app-acquisition to detect emulators and download apps
4. Run /bounty-recon for prioritization + recon pipeline + agent deployment
5. Run /bounty-validation for PoC validation + pre-submission gate
6. Generate HackerOne-formatted reports
```

## Workflows

**Option 1: HackerOne URL**
```
- [ ] Fetch program data and guidelines
- [ ] Download scope CSV
- [ ] Parse eligible assets
- [ ] Deploy agents in parallel
- [ ] Validate PoCs
- [ ] Generate submissions
```

**Option 2: CSV File**
```
- [ ] Parse CSV scope file
- [ ] Extract eligible_for_submission=true assets
- [ ] Collect program guidelines
- [ ] Deploy agents
- [ ] Validate and generate reports
```

## Scope CSV Format

Expected columns:
- `identifier` - Asset URL/domain
- `asset_type` - URL, WILDCARD, API, CIDR
- `eligible_for_submission` - Must be "true"
- `max_severity` - critical, high, medium, low
- `instruction` - Asset-specific notes

Use `tools/csv_parser.py` to parse.

## Shared Workflows

- **Prioritization + Recon + Agent Deployment**: See `/bounty-recon`
- **Mobile App Download**: See `/mobile-app-acquisition`
- **Validation + Compliance + Quality**: See `/bounty-validation`

## Report Format

Required sections (HackerOne standard):
1. Summary (2-3 sentences)
2. Severity (CVSS + business impact)
3. Steps to Reproduce (numbered, clear)
4. Raw HTTP requests/responses (text format)
5. Visual Evidence (screenshots/video)
6. Impact (realistic attack scenario)
7. Remediation (actionable fixes)

Use `tools/report_validator.py` to validate.

## Output Structure

Per OUTPUT.md - Bug Bounty format:

```
outputs/<program>/
├── apps/                         # Downloaded mobile apps
│   ├── <package>.apk
│   └── <bundle>.ipa
├── findings/
│   ├── finding-001/
│   │   ├── report.md           # HackerOne report
│   │   ├── poc.py              # Validated PoC
│   │   ├── poc_output.txt      # Proof
│   │   └── workflow.md         # Manual steps
├── reports/
│   ├── submissions/
│   │   ├── H1_CRITICAL_001.md  # Ready to submit
│   │   └── H1_HIGH_001.md
│   └── SUBMISSION_GUIDE.md
└── evidence/
    ├── screenshots/
    └── http-logs/
```

## Program Selection

**High-Value**:
- New programs (< 30 days)
- Fast response (< 24 hours)
- High bounties (Critical: $5,000+)
- Large attack surface

**Avoid**:
- Slow response (> 1 week)
- Low bounties (Critical: < $500)
- Overly restrictive scope

## Critical Rules

**MUST DO**:
- Validate ALL PoCs before reporting
- Sanitize sensitive data
- Test only `eligible_for_submission=true` assets
- Follow program-specific guidelines
- Compute CVSS scores using a calculator (Python/bash), never guess or estimate

**NEVER**:
- Report without validated PoC
- Test out-of-scope assets
- Include real user data
- Cause service disruption

## Tools

- `tools/csv_parser.py` - Parse HackerOne scope CSVs
- `tools/report_validator.py` - Validate report completeness
- `/pentest` skill - Core testing functionality
- `/bounty-recon` skill - Recon pipeline + agent deployment
- `/bounty-validation` skill - Validation + compliance + quality
- `/mobile-app-acquisition` skill - Mobile app download from emulators
- `/mobile-security` skill - Mobile app analysis
- `/burp-suite` skill - Active scanning, Collaborator OOB testing (via bounty-recon)
- `/hexstrike` skill - 150+ security tools for parallel recon and testing
- `/authenticating` skill - Auth bypass, 2FA, CAPTCHA testing
- `dom-xss-scanner` agent - Automated DOM XSS via Playwright (auto for JS targets)
- **Utility agents**: `patt-fetcher`, `script-generator`, `pentester-validator`

## Integration

Uses `/pentest` skill and Pentester agent. Follows OUTPUT.md for submission format.

## Common Rejections

**Out of Scope**: Check `eligible_for_submission=true`
**By Design / Not a Bug**: The reported behavior is the intended functionality of the service. ALWAYS verify business logic before reporting — understand what the company does and whether the "vulnerability" is actually their core product feature.
**Cannot Reproduce**: Validate PoC, include poc_output.txt
**Duplicate**: Search disclosed reports, submit quickly
**Insufficient Impact**: Show realistic attack scenario

## Usage

```bash
/hackerone <program_url_or_csv_path>
```
