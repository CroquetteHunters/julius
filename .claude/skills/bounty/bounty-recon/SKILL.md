---
name: bounty-recon
description: Shared bug bounty reconnaissance pipeline - post-enumeration recon (httpx, naabu, ffuf, nuclei), extended recon (parallel skill deployment), conditional specialized testing triggers, agent deployment patterns (pentester, DOM XSS), and chain discovery. Referenced by /intigriti and /hackerone.
---

# Bug Bounty Recon Pipeline

Shared reconnaissance and agent deployment logic for bug bounty platforms. Invoked by `/intigriti` and `/hackerone` after scope parsing.

## Bounty-Driven Prioritization (MANDATORY FIRST STEP)

**BEFORE any testing, read the program scope and create a prioritized attack plan.**

1. **Parse scope completely FIRST**: Extract from the program page (PDF/URL/CSV/manual):
   - In-scope assets with their tiers/eligibility, severity caps, and instructions
   - Bounty table (amounts per severity per tier)
   - Program's stated worst-case scenarios or priority vulnerability types
   - **Full out-of-scope list** (application-level AND mobile/desktop-specific exclusions)
   - Any program-specific rules or testing limitations
2. **Map each vuln type to the program's bounty table**: Use the ACTUAL reward amounts from this specific program — don't assume generic values. Rank attack vectors from highest to lowest payout.
3. **Start with the program's stated worst-case scenarios** — these are what the triagers care about most and signal what they'll pay top bounty for
4. **Cross-reference every planned test against the OOS list** BEFORE executing it. If a vuln type is excluded, don't waste time testing it regardless of how easy it might be to find.
5. **Chain findings for impact escalation** — a low-severity finding chained with another can reach Critical. Always think about chains that multiply impact.
6. **Drop low-impact findings quickly** if they don't chain into something bigger
7. **Check mobile/desktop-specific exclusions separately** — programs often have a dedicated exclusion list for mobile that differs from web. Read it before any APK/IPA analysis.

**Present the prioritized plan to the user BEFORE starting any testing.**

## Endpoint Recon (historical URL discovery)

Run `tools/recox/endpoint_recon.py` to discover historical endpoints from Wayback Machine, Common Crawl, OTX, and URLScan:

```bash
# Full recon for a domain
python3 tools/recox/endpoint_recon.py target.com -o outputs/<program>/recon/endpoints.txt

# Interesting files only (js, json, xml, php, config, env, etc.)
python3 tools/recox/endpoint_recon.py target.com -i -o outputs/<program>/recon/endpoints_interesting.txt

# Specific sources only
python3 tools/recox/endpoint_recon.py target.com --sources wayback,otx
```

Feed discovered endpoints to pentester agents for targeted testing (hidden admin panels, old API versions, exposed config files).

## Post-Enumeration Recon Pipeline (for domain/wildcard assets)

**BEFORE deploying pentester agents**, run this pipeline on wildcard/domain assets to identify the real attack surface:

1. **httpx** live host detection: `httpx -l subs.txt -sc -title -tech-detect -timeout 5 -threads 50 -retries 0`
   - Pre-filter `.internal.*`/`.uat.*` subdomains (cause DNS hangs)
   - Categorize hosts by response code and tech stack
2. **naabu** port scan: `naabu -list hostnames.txt -top-ports 1000` (bare hostnames, NOT URLs)
   - Focus on non-standard ports (not 80/443) — admin panels, dev servers
3. **ffuf** directory fuzzing: `ffuf -w ~/SecLists/Discovery/Web-Content/common.txt -u "https://{host}/FUZZ" -mc 200,301,302`
   - Target non-Cloudflare hosts; filter CF WAF 403s with `-fs 5453`
4. **nuclei** vuln scan: `nuclei -l live.txt -severity medium,high,critical -timeout 10`
   - Run in background (~10-15 min); review for false positives

See `/subdomain_enumeration` skill for detailed lessons learned and gotchas.

## Extended Recon (AUTOMATIC, parallel with post-enumeration pipeline)

Deploy these skills **in parallel** during recon to expand attack surface and inform pentester agents:

1. **`/code-repository-intel`** — Scan GitHub/GitLab for public repos, leaked secrets, CI configs, dependency files. High-value: exposed `.env`, API keys in commit history, internal endpoints in CI pipelines.
2. **`/api-portal-discovery`** — Discover public API portals, developer docs, OpenAPI/Swagger specs. Endpoints found here bypass WAF and often lack rate limiting.
3. **`/web-application-mapping`** — Comprehensive endpoint discovery via passive browsing + headless automation. Maps forms, AJAX calls, WebSocket connections, and hidden functionality.
4. **`/security-posture-analyzer`** — Enumerate security headers (CSP, HSTS, X-Frame-Options), WAF presence, and security.txt. Results directly inform payload selection and bypass strategy.
5. **`/cdn-waf-fingerprinter`** — Identify CDN (Cloudflare, Akamai, Fastly) and WAF. Critical for: filtering ffuf results, selecting XSS payloads that bypass WAF rules, identifying origin IP bypass opportunities.

**Feed results to pentester agents**: All discovered endpoints, API specs, security posture data, and WAF fingerprints are passed as context to each Pentester agent to enable targeted testing.

## Agent Deployment

**Pentester Agent** per asset (tier-prioritized):
- Tier 1 / highest-bounty assets: Deploy first, allocate most resources
- Tier 2-3 assets: Deploy in parallel, standard resources
- Tier 4-5 / lowest assets: Deploy last, lower priority
- Has access to `patt-fetcher` agent for on-demand PayloadsAllTheThings payloads (30+ categories: SQLi, XSS, SSTI, SSRF, deserialization, OAuth, etc.)
- Has access to `script-generator` agent for optimized PoC scripts (>30 lines, parallelized, syntax-validated)

**Mobile assets**: Deploy `/mobile-security` skill agents after app download (see `/mobile-app-acquisition`)

**DOM XSS scanning (AUTOMATIC for JS-heavy targets)**:
When httpx tech-detect or page analysis reveals JavaScript frameworks (React, Vue, Angular, jQuery, Next.js, Nuxt, SvelteKit) or the target is a SPA:
- Deploy `dom-xss-scanner` agent **in parallel** with the Pentester agent for that asset
- The scanner hooks sinks (innerHTML, document.write, eval, jQuery.html), injects canaries through all DOM sources, and detects taint flow automatically
- Findings feed back into the Pentester agent's results for chain analysis
- Trigger criteria: httpx `tech-detect` output contains JS framework names, OR page has `<div id="app">`, `data-reactroot`, `ng-app`, `[data-v-]`, OR `Content-Type` indicates SPA (HTML shell + JS bundles)

**Parallel Execution**:
- N assets = N Pentester Orchestrators + dom-xss-scanner where applicable
- Each spawns specialized agents
- Tier 1 findings reviewed first
- Mobile app analysis + DOM XSS scanning run alongside web testing

## Conditional Specialized Testing (AUTOMATIC based on recon results)

Deploy these skills when recon or tech detection identifies specific conditions:

- **`/cve-testing`** + **`/cve-poc-generator`** — When httpx, nuclei, or tech-detect identifies specific software versions (e.g., Apache 2.4.49, jQuery 3.4.1, Spring 5.3.x). `/cve-testing` researches known CVEs and tests with public exploits. When a CVE is confirmed, `/cve-poc-generator` creates a standalone Python PoC script + detailed report with NVD data, CVSS vector, and remediation. High-value: unpatched services on non-standard ports.
- **`/source-code-scanning`** — When `/code-repository-intel` discovers exposed source code (public repos, leaked repos, `.git` directories, source maps). Runs SAST for OWASP Top 10 + CWE Top 25, scans dependencies for CVEs, detects hardcoded secrets (API keys, tokens, passwords), and identifies insecure patterns. Chain: exposed secrets → account takeover, dependency CVEs → RCE.
- **`/ai-threat-testing`** — When recon discovers AI/LLM features: chatbots, AI assistants, `/api/chat`, `/api/completions`, prompt-based interfaces, or OpenAI/Anthropic SDK references in JS bundles. Tests OWASP LLM Top 10 (prompt injection, model extraction, data poisoning).
- **`/authenticating`** — When login/signup forms are discovered. Automates credential testing, 2FA bypass, CAPTCHA solving, session management analysis via Playwright MCP. Deploy for each unique auth endpoint found.
- **`/cloud-security`** — When `/cloud-infra-detector` or recon identifies AWS/Azure/GCP infrastructure (S3 buckets, Azure blobs, metadata endpoints, cloud-specific headers). Tests IAM misconfigs, storage enumeration, SSRF to metadata service.
- **`/container-security`** — When Kubernetes/Docker indicators are found (K8s headers, `/healthz` endpoints, container orchestration signals, `.docker` files in repos). Tests RBAC, pod security, network policies, container escape vectors.
- **`/burp-suite`** — When Burp Suite MCP is available. Deploy for active scanning + Collaborator OOB testing on high-value endpoints. Essential for blind XSS, blind SSRF, and out-of-band data exfiltration detection.

## Chain Discovery (DURING testing)

- After each finding, actively evaluate: "Can this chain with another finding to escalate severity?"
- Common high-value chains: open redirect + OAuth = ATO, SSRF + cloud metadata = credential theft, XSS + CSRF = stored ATO
- When a chain opportunity is identified, prioritize testing the complementary finding immediately
- Document chain potential in findings even if the complementary vuln hasn't been confirmed yet
