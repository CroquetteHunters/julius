# Julius - AI Security Testing Toolkit

<div align="center">

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Claude AI](https://img.shields.io/badge/Powered%20by-Claude%20AI-blue)](https://claude.ai)
[![GitHub issues](https://img.shields.io/github/issues/CroquetteHunters/julius)](https://github.com/CroquetteHunters/julius/issues)

**Claude Code skills, agents, and tools for penetration testing, bug bounty hunting, and vulnerability management**

</div>

---

## What is Julius?

Julius is a security testing toolkit built as **Claude Code skills and agents**. It provides AI-orchestrated workflows for pentesting, bug bounty programs, and vulnerability management — all invoked via slash commands inside Claude Code.

Built on top of [Transilience AI Community Tools](https://github.com/transilienceai/communitytools).

### At a glance

| | |
|-|-|
| **47 skills** | Pentesting, recon, bug bounty, cloud, mobile, SAST, reporting |
| **6 agents** | DOM XSS scanner, finding validator, script generator, payload fetcher, HackTheBox, skill creator |
| **186 attack docs** | PortSwigger Academy solutions, cheat sheets, methodology guides |
| **38+ engagements** | Active bug bounty and pentest outputs (gitignored) |
| **3 bug bounty platforms** | HackerOne, Intigriti, DefectDojo |
| **Tool integrations** | Burp Suite MCP, HexStrike AI, Playwright, Kali toolset |

---

## Architecture

Following [Vercel's research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals), Julius uses a hybrid architecture:

- **`AGENTS.md`** — Always loaded. Compressed security knowledge: vulnerability payloads, CVSS reference, methodology frameworks (PTES, OWASP, MITRE), bug bounty reporting policy.
- **Skills** (`.claude/skills/`) — User-triggered via `/skill-name`. Handle multi-step orchestration, parallel agent deployment, user approval gates, and reporting workflows.
- **Agents** (`.claude/agents/`) — Reusable specialized subprocesses spawned by skills for focused tasks.

```
julius/
├── AGENTS.md                        # Passive knowledge base (always loaded)
├── CLAUDE.md                        # Repository instructions
├── .claude/
│   ├── skills/
│   │   ├── pentest/                 # Core pentesting — 11 attack categories, 186 docs
│   │   ├── offensive/               # Targeted testing skills
│   │   │   ├── ai-threat-testing/       # OWASP LLM Top 10
│   │   │   ├── authenticating/          # Auth, 2FA, CAPTCHA, bot evasion
│   │   │   ├── common-appsec-patterns/  # OWASP Top 10 quick testing
│   │   │   ├── cve-testing/             # Known CVE testing
│   │   │   ├── cve-poc-generator/       # CVE research + PoC generation
│   │   │   └── source-code-scanning/    # SAST + dependency CVE scanning
│   │   ├── recon/                   # Reconnaissance (10 skills)
│   │   │   ├── domain-assessment/       # Subdomain discovery + port scanning
│   │   │   ├── web-application-mapping/ # Endpoint discovery, tech detection
│   │   │   ├── subdomain-enumeration/   # CT logs, passive DNS, dorks
│   │   │   ├── dns-intelligence/        # MX, TXT, NS, CNAME, SRV analysis
│   │   │   └── ...                      # + 6 more recon skills
│   │   ├── detection/               # Technology detection (15 skills)
│   │   │   ├── frontend-inferencer/     # React, Angular, Vue detection
│   │   │   ├── backend-inferencer/      # Server/framework/CMS detection
│   │   │   ├── cdn-waf-fingerprinter/   # Cloudflare, Akamai, WAFs
│   │   │   └── ...                      # + 12 more detection skills
│   │   ├── bounty/                  # Bug bounty workflows
│   │   │   ├── hackerone/               # HackerOne automation
│   │   │   ├── intigriti/               # Intigriti automation (API, tiers)
│   │   │   ├── bounty-recon/            # Shared recon pipeline
│   │   │   ├── bounty-validation/       # Shared validation + anti-hallucination
│   │   │   └── mobile-app-acquisition/  # APK/IPA download from emulators
│   │   ├── infrastructure/          # Cloud, container, mobile security
│   │   │   ├── cloud-security/          # AWS, Azure, GCP
│   │   │   ├── container-security/      # Docker, Kubernetes
│   │   │   └── mobile-security/         # MobSF + Frida
│   │   ├── tools/                   # Tool integrations
│   │   │   ├── burp-suite/              # Burp Suite MCP
│   │   │   ├── hexstrike/               # HexStrike AI (150+ tools)
│   │   │   └── defectdojo/             # DefectDojo vuln management
│   │   ├── reporting/               # Output and reporting
│   │   │   ├── evidence-formatter/
│   │   │   ├── json-report-generator/
│   │   │   └── report-exporter/
│   │   └── skiller/                 # Skill creation and management
│   │
│   └── agents/                      # 6 reusable agents
│       ├── dom-xss-scanner.md       # Automated DOM XSS via Playwright
│       ├── pentester-validator.md   # Anti-hallucination finding validation
│       ├── script-generator.md      # Optimized PoC script generation
│       ├── patt-fetcher.md          # PayloadsAllTheThings fetcher
│       ├── hackthebox.md            # HackTheBox challenge orchestrator
│       └── skiller.md               # Skill creation automation
│
├── tools/                           # External tool installers + scripts
│   ├── playwright/                  # Browser automation setup
│   ├── kali/                        # nmap, ffuf, sqlmap, nikto, etc.
│   └── recox/                       # Wayback/CommonCrawl endpoint discovery
│
├── outputs/                         # Engagement outputs (gitignored)
├── templates/                       # Skill templates
└── CONTRIBUTING.md
```

---

## Core Skills

### Penetration Testing

```bash
/pentest
```

The main skill. Runs a 6-phase pentest:

1. **Initialization** — Scope, engagement folder
2. **Reconnaissance** — Subdomain enum, port scanning, tech detection
3. **Planning** — Test plan → user approval gate
4. **Testing** — Parallel agents across 11 attack categories (40+ attack types)
5. **Aggregation** — Dedup, chain discovery, severity calculation
6. **Reporting** — Findings with CVSS, CWE, evidence, remediation

**Attack categories:**

| Category | Types |
|----------|-------|
| Injection | SQL, NoSQL, command, SSTI, XXE |
| Client-side | XSS (reflected/stored/DOM), CSRF, clickjacking, CORS, prototype pollution |
| Server-side | SSRF, HTTP smuggling, file upload, path traversal, deserialization, race conditions, cache poisoning, access control, business logic, host header, info disclosure, web cache deception |
| Authentication | JWT, OAuth, auth bypass, password attacks, default credentials |
| API | GraphQL, REST, WebSockets, Web LLM |
| Cloud/Containers | AWS, Azure, GCP, Docker, Kubernetes |
| Infrastructure | DNS, port scanning, MITM, SMB/NetBIOS |

### Bug Bounty

```bash
/hackerone    # HackerOne programs — scope CSV parsing, parallel testing, platform-ready reports
/intigriti    # Intigriti programs — API scope fetch, tier prioritization, EU-formatted reports
```

Both share:
- `/bounty-recon` — Recon pipeline: httpx, naabu, ffuf, nuclei, endpoint recon, parallel skill deployment
- `/bounty-validation` — 5-point anti-hallucination validation, OOS checks, business logic verification, AI compliance disclosure

**Active programs** (from `outputs/`): Tomorrowland, NVIDIA, Yahoo, Capital.com, Miro, Bitvavo, DataCamp, Revolut, Rivian, Grafana, Generali, Hitta, DigitalOcean, Rosenberger, ST, BMW, CaixaBank, AS Watson, Madrid...

### Vulnerability Management

```bash
/defectdojo <product> [engagement]
```

- Phase 1: Write findings locally as `report.md` with YAML frontmatter → user reviews
- Phase 2: Upload to DefectDojo REST API v2 (after explicit approval)
- Google Cloud IAP authentication via Playwright
- CWE mapping, evidence upload, deduplication
- Findings created as `active=false, verified=false` — user must review in DefectDojo

### Source Code Review

```bash
/source-code-scanning
```

SAST scanning: OWASP Top 10, CWE Top 25, hardcoded secrets, dependency CVEs, insecure patterns. Produces DefectDojo-compatible findings with `file_path`, `line`, `sast_source_*` fields.

### Specialized Testing

| Skill | Command | What it does |
|-------|---------|-------------|
| Cloud Security | `/cloud-security` | AWS/Azure/GCP — IAM, storage, serverless, CIS Benchmarks |
| Container Security | `/container-security` | Docker image scanning, K8s RBAC, pod security, escape testing |
| Mobile Security | `/mobile-security` | MobSF static + Frida dynamic (OWASP Mobile Top 10) |
| AI/LLM Threats | `/ai-threat-testing` | OWASP LLM Top 10 — prompt injection, model extraction, data poisoning |
| Auth Testing | `/authenticating` | Signup/login automation, 2FA bypass, CAPTCHA solving, bot evasion |
| CVE Testing | `/cve-testing` | Known CVE testing with public exploits |
| CVE PoC Generator | `/cve-poc-generator` | Research CVE → generate Python PoC + report |

### Reconnaissance (19 skills)

Lightweight coordinator skills that run recon tools or orchestrate other skills:

`/domain-assessment` `/web-application-mapping` `/subdomain-enumeration` `/dns-intelligence` `/certificate-transparency` `/http-fingerprinting` `/tls-certificate-analysis` `/security-posture-analyzer` `/cdn-waf-fingerprinter` `/frontend-inferencer` `/backend-inferencer` `/cloud-infra-detector` `/devops-detector` `/third-party-detector` `/ip-attribution` `/domain-discovery` `/code-repository-intel` `/job-posting-analysis` `/web-archive-analysis`

---

## Agents

Agents are specialized subprocesses spawned by skills:

| Agent | Purpose |
|-------|---------|
| **dom-xss-scanner** | Injects canary tokens through DOM sources, hooks sinks, detects taint flow, escalates with context-aware payloads |
| **pentester-validator** | Anti-hallucination: CVSS consistency, evidence existence, PoC syntax, claims-vs-evidence corroboration |
| **script-generator** | Generates parallelized, syntax-validated PoC scripts (>30 lines) |
| **patt-fetcher** | Fetches PayloadsAllTheThings payloads on demand (30+ categories) |
| **hackthebox** | Orchestrates HackTheBox challenges — VPN, login, solving, writeup |
| **skiller** | Automated skill directory creation and validation |

---

## Tool Integrations

| Tool | Integration | Used for |
|------|-------------|----------|
| **Burp Suite** | MCP (PortSwigger) | Active scanning, Collaborator OOB, traffic replay, sitemap |
| **HexStrike AI** | MCP server | 150+ tools: network, web, binary, cloud, auth |
| **Playwright** | MCP | DOM XSS, auth testing, screenshot evidence, client-side validation |
| **Kali tools** | CLI | nmap, ffuf, sqlmap, nikto, gobuster, testssl, dig |
| **recox_endpoint_recon.py** | Script | Wayback Machine, Common Crawl, OTX, URLScan endpoint discovery |

---

## Quick Start

```bash
# Clone
git clone https://github.com/CroquetteHunters/julius.git
cd julius

# Open in Claude Code
claude .

# Run a pentest
/pentest

# Run a bug bounty program
/intigriti

# Create a new skill
/skiller
```

Skills auto-load from `.claude/skills/`. No additional configuration needed.

### Optional tool setup

```bash
# Kali tools (nmap, ffuf, sqlmap, nikto...)
bash tools/kali/install.sh

# Playwright (browser automation)
bash tools/playwright/install.sh
```

---

## Output Structure

All engagements produce outputs in `outputs/<engagement>/` (gitignored):

```
outputs/{engagement}/
├── report/                    # Final deliverables
│   ├── Penetration-Test-Report.docx
│   ├── pentest-report.json
│   └── appendix/
└── processed/                 # Working files
    ├── reconnaissance/        # Recon results
    ├── findings/              # Individual findings
    │   └── finding-001/
    │       ├── report.md      # YAML frontmatter + markdown
    │       ├── poc.py         # Proof of concept
    │       ├── poc_output.txt # PoC execution output
    │       └── evidence/      # Screenshots, HTTP logs
    └── activity/              # NDJSON logs
```

---

## Bug Bounty Reporting Rules

Enforced across all bug bounty skills:

- **No PoC = No Report** — Every finding needs a working exploit demo
- **CVSS must be calculated** — Never guessed. Use Python/bash calculator
- **AI disclosure mandatory** — All reports include AI usage transparency
- **Validation gate** — pentester-validator agent checks: CVSS consistency, evidence existence, PoC syntax, claims corroboration
- **Business logic verification** — Verify findings are not "by design" before reporting
- **Out of scope** — CORS, missing headers, self-XSS, version disclosure, rate limiting (unless ATO), username enumeration

---

## Contributing

```bash
# Automated (recommended)
/skiller

# Manual
gh issue create --title "Add skill: X" --body "Description..."
git checkout -b feature/skill-name
# Develop, test, commit with conventional format
# feat(scope): description | fix(scope): description
git push && gh pr create
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## Upstream

Fork of [Transilience AI Community Tools](https://github.com/transilienceai/communitytools). Upstream changes synced periodically.

---

## License

MIT — See [LICENSE](LICENSE).

---

<div align="center">

**Built on [Transilience AI Community Tools](https://github.com/transilienceai/communitytools)**

[Report Issue](https://github.com/CroquetteHunters/julius/issues) | [Upstream](https://github.com/transilienceai/communitytools)

</div>
