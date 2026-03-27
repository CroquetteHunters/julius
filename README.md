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
| **2 bug bounty platforms** | HackerOne, Intigriti |
| **Vulnerability management** | DefectDojo integration (IAP auth, API import, evidence upload) |
| **Tool integrations** | Burp Suite MCP, HexStrike AI (150+ tools), Playwright, Kali toolset, RecoX |

---

## Bug Bounty Workflow

The primary use case. Two entry points depending on platform:

```bash
/intigriti <program_url_or_pdf>    # Intigriti programs (API scope fetch, tier prioritization)
/hackerone <program_url_or_csv>    # HackerOne programs (CSV scope parsing)
```

### What happens when you run `/intigriti` or `/hackerone`

```
1. SCOPE PARSING
   Parse program scope → extract assets, tiers, bounty table, OOS list
   Present prioritized attack plan → user approves before testing starts

2. RECONNAISSANCE (bounty-recon)
   ├── Endpoint recon: tools/recox (Wayback, CommonCrawl, OTX, URLScan)
   ├── Post-enumeration: httpx → naabu → ffuf → nuclei
   ├── Extended recon (parallel skills):
   │   ├── /code-repository-intel     — GitHub/GitLab leaked secrets, CI configs
   │   ├── /api-portal-discovery      — OpenAPI/Swagger specs, dev docs
   │   ├── /web-application-mapping   — Headless browsing, endpoint discovery
   │   ├── /security-posture-analyzer — Headers, CSP, WAF, security.txt
   │   ├── /cdn-waf-fingerprinter     — CDN/WAF identification for bypass strategy
   │   └── /hexstrike                 — 150+ tools for large-scope parallel recon
   └── Conditional triggers (based on recon results):
       ├── /cve-testing + /cve-poc-generator  — When specific software versions found
       ├── /source-code-scanning              — When exposed source code found
       ├── /ai-threat-testing                 — When AI/LLM features detected
       ├── /authenticating                    — When login forms discovered
       ├── /cloud-security                    — When AWS/Azure/GCP infra detected
       ├── /container-security                — When K8s/Docker indicators found
       └── /burp-suite                        — Active scanning + Collaborator OOB

3. TESTING (parallel agents per asset, tier-prioritized)
   ├── Pentester agents: 40+ attack types across 11 categories
   ├── DOM XSS scanner: auto-deployed for JS-heavy targets (React, Vue, Angular)
   ├── patt-fetcher: on-demand PayloadsAllTheThings payloads
   ├── script-generator: PoC scripts (>30 lines, parallelized, syntax-validated)
   └── /mobile-security: MobSF + Frida for mobile assets

4. VALIDATION (bounty-validation)
   ├── Every finding requires: poc.py + poc_output.txt + evidence/
   ├── pentester-validator agent: CVSS consistency, evidence check, PoC syntax
   ├── Business logic verification: is this "by design"?
   ├── OOS check: cross-reference against program exclusions
   └── AI disclosure section (mandatory)

5. SUBMISSION
   Platform-ready reports with CVSS, CWE, steps to reproduce, remediation
```

### Bug bounty rules (enforced)

- **No PoC = No Report** — Every finding needs a working exploit demo
- **CVSS must be calculated** — Never guessed. Use Python/bash calculator
- **Business logic verification** — Verify findings are not "by design" before reporting
- **AI disclosure mandatory** — All reports include AI usage transparency
- **Out of scope** — CORS, missing headers, self-XSS, version disclosure, rate limiting (unless ATO), username enumeration

---

## DefectDojo Workflow

Separate from bug bounty. Used for internal pentests, code reviews, and vulnerability management.

```bash
/defectdojo <product> [engagement]
```

### Workflow

```
1. AUTHENTICATE
   ├── Reads DEFECTDOJO_URL + DEFECTDOJO_TOKEN env vars
   └── Google Cloud IAP auth via Playwright (cookie cache with ~1h TTL)

2. TESTING (using /pentest, /source-code-scanning, or manual review)
   Run your security assessment — pentest, code review, or scan

3. LOCAL REPORTS (Phase 1 — always before any upload)
   ├── Each finding → outputs/defectdojo-{engagement}/findings/finding-NNN/report.md
   ├── YAML frontmatter: title, cwe, cvssv3, severity, endpoint or file_path
   ├── Markdown body: Description, Impact, Steps to Reproduce, Mitigation
   ├── Evidence: screenshots, PoC scripts, HTTP logs in evidence/
   └── Present summary table → user reviews locally

4. UPLOAD (Phase 2 — only after explicit user approval)
   ├── Create "Manual Review" test in engagement
   ├── Import findings with CWE mapping and evidence
   ├── Findings created as active=false, verified=false (user reviews in DD)
   └── Deduplication against existing findings
```

### Finding sources DefectDojo supports

| Source | How |
|--------|-----|
| Manual pentest | Option 1: Security code review → local reports → upload |
| Pentest findings | Option 2: Read from `outputs/{engagement}/findings/` |
| Scanner output | Option 3: Reimport nuclei, ZAP, Burp, Trivy, Semgrep, etc. (150+ formats) |
| CVE PoCs | Option 5: Import from `outputs/processed/cve-pocs/` |
| Source code scanning | Option 6: SAST findings with `static_finding=true`, `file_path`, `sast_source_*` fields |

### SAST fields for code review findings

```yaml
---
title: "SSRF via unvalidated URL input"
cwe: 918
cvssv3: "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N"
cvssv3_score: 7.5
severity: High
static_finding: true
dynamic_finding: false
file_path: "src/app/Domain/Action.php"
line: 42
sast_source_file_path: "src/app/Http/Controllers/ExampleController.php"
sast_source_line: 15
sast_source_object: "$request->input('url')"
sast_sink_object: "Http::get()"
---
```

---

## Pentest Skill

```bash
/pentest
```

6-phase pentest orchestrator with 40+ attack types across 11 categories:

| Category | Types |
|----------|-------|
| Injection | SQL, NoSQL, command, SSTI, XXE |
| Client-side | XSS (reflected/stored/DOM), CSRF, clickjacking, CORS, prototype pollution |
| Server-side | SSRF, HTTP smuggling, file upload, path traversal, deserialization, race conditions, cache poisoning, access control, business logic, host header, info disclosure, web cache deception |
| Authentication | JWT, OAuth, auth bypass, password attacks, default credentials |
| API | GraphQL, REST, WebSockets, Web LLM |
| Cloud/Containers | AWS, Azure, GCP, Docker, Kubernetes |
| Infrastructure | DNS, port scanning, MITM, SMB/NetBIOS |

Each attack type has PortSwigger Academy solutions, cheat sheets, and methodology docs in `.claude/skills/pentest/attacks/`.

---

## Other Skills

### Offensive Testing

| Skill | Command | What it does |
|-------|---------|-------------|
| Source Code Scanning | `/source-code-scanning` | SAST: OWASP Top 10, CWE Top 25, secrets, dependency CVEs |
| AI/LLM Threats | `/ai-threat-testing` | OWASP LLM Top 10 — prompt injection, model extraction |
| Auth Testing | `/authenticating` | Signup/login automation, 2FA bypass, CAPTCHA, bot evasion |
| CVE Testing | `/cve-testing` | Known CVE testing with public exploits |
| CVE PoC Generator | `/cve-poc-generator` | Research CVE → Python PoC + report |
| OWASP Quick Test | `/common-appsec-patterns` | OWASP Top 10 quick-hit testing |

### Infrastructure

| Skill | Command | What it does |
|-------|---------|-------------|
| Cloud Security | `/cloud-security` | AWS/Azure/GCP — IAM, storage, serverless, CIS Benchmarks |
| Container Security | `/container-security` | Docker/K8s — RBAC, pod security, escape testing |
| Mobile Security | `/mobile-security` | MobSF static + Frida dynamic (OWASP Mobile Top 10) |

### Reconnaissance (10 skills)

`/domain-assessment` `/web-application-mapping` `/subdomain-enumeration` `/dns-intelligence` `/certificate-transparency` `/domain-discovery` `/code-repository-intel` `/api-portal-discovery` `/job-posting-analysis` `/web-archive-analysis`

### Technology Detection (15 skills)

`/frontend-inferencer` `/backend-inferencer` `/http-fingerprinting` `/tls-certificate-analysis` `/cdn-waf-fingerprinter` `/cloud-infra-detector` `/devops-detector` `/third-party-detector` `/ip-attribution` `/security-posture-analyzer` `/html-content-analysis` `/javascript-dom-analysis` `/confidence-scorer` `/conflict-resolver` `/signal-correlator`

---

## Tool Integrations

| Tool | Integration | Used for |
|------|-------------|----------|
| **Burp Suite** | MCP (PortSwigger) | Active scanning, Collaborator OOB, traffic replay, sitemap |
| **HexStrike AI** | MCP server | 150+ tools: nmap, nuclei, sqlmap, gobuster, subfinder, etc. |
| **Playwright** | MCP | DOM XSS, auth testing, screenshot evidence, IAP auth |
| **Kali tools** | CLI | nmap, ffuf, sqlmap, nikto, gobuster, testssl, dig |
| **RecoX** | Script | Wayback Machine, Common Crawl, OTX, URLScan endpoint discovery |

---

## Agents

| Agent | Purpose |
|-------|---------|
| **dom-xss-scanner** | Injects canary tokens through DOM sources, hooks sinks, detects taint flow |
| **pentester-validator** | Anti-hallucination: CVSS consistency, evidence existence, PoC syntax, claims corroboration |
| **script-generator** | Generates parallelized, syntax-validated PoC scripts (>30 lines) |
| **patt-fetcher** | Fetches PayloadsAllTheThings payloads on demand (30+ categories) |
| **hackthebox** | Orchestrates HackTheBox challenges — VPN, login, solving, writeup |
| **skiller** | Automated skill directory creation and validation |

---

## Quick Start

```bash
# Clone
git clone https://github.com/CroquetteHunters/julius.git
cd julius

# Open in Claude Code
claude .

# Bug bounty
/intigriti <program_url>
/hackerone <scope_csv>

# Internal pentest
/pentest

# Import findings to DefectDojo
/defectdojo <product> <engagement>

# Source code review
/source-code-scanning
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

## Repository Structure

```
julius/
├── AGENTS.md                        # Passive knowledge base (always loaded)
├── CLAUDE.md                        # Repository instructions
├── .claude/
│   ├── skills/
│   │   ├── pentest/                 # 11 attack categories, 186 docs
│   │   ├── offensive/               # SAST, CVE, auth, AI threats (6 skills)
│   │   ├── recon/                   # Reconnaissance (10 skills)
│   │   ├── detection/               # Technology detection (15 skills)
│   │   ├── bounty/                  # HackerOne, Intigriti, shared pipelines (5 skills)
│   │   ├── infrastructure/          # Cloud, container, mobile (3 skills)
│   │   ├── tools/                   # Burp Suite, HexStrike, DefectDojo (3 skills)
│   │   ├── reporting/               # Formatters and exporters (3 skills)
│   │   └── skiller/                 # Skill creation
│   └── agents/                      # 6 reusable agents
├── tools/                           # Playwright, Kali, RecoX installers
├── outputs/                         # Engagement outputs (gitignored)
└── CONTRIBUTING.md
```

---

## Contributing

```bash
/skiller    # Automated skill creation

# Or manually:
git checkout -b feature/skill-name
# feat(scope): description | fix(scope): description
```

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Upstream

Fork of [Transilience AI Community Tools](https://github.com/transilienceai/communitytools).

## License

MIT — See [LICENSE](LICENSE).

---

<div align="center">

**Built on [Transilience AI Community Tools](https://github.com/transilienceai/communitytools)**

[Report Issue](https://github.com/CroquetteHunters/julius/issues) | [Upstream](https://github.com/transilienceai/communitytools)

</div>
