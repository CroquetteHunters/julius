---
name: subdomain-enumeration
description: Enumerates subdomains using CT logs, passive DNS, and search engine dorks
tools: Bash, WebFetch
model: inherit
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "../../../../hooks/skills/pre_network_skill_hook.sh"
        - type: command
          command: "../../../../hooks/skills/pre_rate_limit_hook.sh"
  PostToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "../../../../hooks/skills/post_skill_logging_hook.sh"
---

# Subdomain Enumeration Skill

## Purpose

Enumerate all discoverable subdomains for a given domain using passive reconnaissance techniques including Certificate Transparency logs, passive DNS, and search engine dorks.

## Operations

### 1. query_crt_sh

Query Certificate Transparency logs via crt.sh API.

**Endpoint:**
```
GET https://crt.sh/?q=%25.{domain}&output=json
```

**Process:**
1. URL encode the wildcard query
2. Make HTTP GET request
3. Parse JSON response
4. Extract unique subdomains from name_value field
5. Deduplicate and sort results

**Example Response:**
```json
[
  {
    "issuer_ca_id": 183267,
    "issuer_name": "C=US, O=Let's Encrypt, CN=R3",
    "common_name": "*.example.com",
    "name_value": "api.example.com\nwww.example.com"
  }
]
```

### 2. search_engine_dorks

Use search engine dorks to discover subdomains.

**Dork Queries:**
```
site:*.{domain} -www
site:{domain} inurl:subdomain
site:*.*.{domain}
```

**Process:**
1. Execute each dork query
2. Extract unique subdomains from results
3. Validate each subdomain resolves
4. Merge with CT log results

### 3. check_common_subdomains

Test a wordlist of common subdomains.

**Common Subdomain Wordlist:**
```
api, app, dev, staging, test, beta, www, mail, webmail,
admin, portal, dashboard, docs, status, support, help,
blog, news, cdn, static, assets, media, img, images,
auth, login, sso, id, account, my, secure, vpn,
git, gitlab, github, jenkins, ci, build, deploy,
k8s, kubernetes, docker, registry, grafana, prometheus,
shop, store, checkout, cart, payments, billing,
crm, erp, hr, internal, intranet, wiki, confluence,
slack, jira, trello, asana, notion, airtable,
aws, azure, gcp, cloud, s3, storage, backup,
mobile, ios, android, m, wap,
v1, v2, v3, api-v1, api-v2, rest, graphql, gql
```

**Process:**
1. For each subdomain in wordlist:
   - Construct FQDN: {subdomain}.{domain}
   - Attempt DNS resolution
   - Record if resolves
2. Return list of valid subdomains

### 4. passive_dns_lookup

Query passive DNS databases (if available).

**Data Sources:**
- VirusTotal (requires API key)
- SecurityTrails (requires API key)
- DNSDumpster (free, limited)

**Note:** This operation is optional and depends on available API access.

### 5. recox_scan

Query RecoX web-based reconnaissance tool for additional subdomain data.

**Endpoint:** `https://recox.hackerz.space/`

**Process:**
1. Use WebFetch to query RecoX with the target domain
2. Parse results for subdomains not found by other sources
3. Merge with crt.sh and wordlist results, deduplicating

**Note:** RecoX complements crt.sh and subfinder by using additional data sources. Always query it alongside other tools to maximize coverage.

## Post-Enumeration Recon Pipeline

After subdomain discovery, run this 4-step pipeline to reduce the attack surface to actionable targets and identify quick wins.

### 6. live_host_detection (httpx)

Probe each subdomain over HTTP/HTTPS to identify live hosts. This is the essential first filter — it reduces the attack surface to only hosts that are actually alive.

**Command:**
```bash
httpx -l {target}_subdomains.txt -sc -title -tech-detect -timeout 5 -threads 50 -retries 0 -o {target}_live.txt
```

**Process:**
1. Feed the merged subdomain list from operations 1-5
2. **IMPORTANT**: Filter out `.internal.*` and `.uat.*` subdomains first — they cause DNS timeout hangs
3. Run in two batches if > 100 subdomains (known-resolving first, then CT-log-only)
4. Parse output for status codes, titles, and tech stacks

**Lessons Learned:**
- Use `-timeout 5 -retries 0` to avoid hanging on unresolvable internal subdomains
- Internal/UAT subdomains (`*.internal.*`, `*.uat.*`, `eu-central-1.*`) will hang indefinitely — pre-filter them
- httpx writes output file only after completion, not progressively
- Most Cloudflare-proxied hosts return 403 (managed challenge) or 404 (catch-all) — note which return 200/301/302 as these have real applications

### 7. port_scanning (naabu)

Fast-scan live targets for open ports beyond 80/443. Non-standard ports often expose admin panels, dev/staging servers, internal APIs, or debug endpoints.

**Command:**
```bash
naabu -list {target}_hostnames.txt -top-ports 1000 -o {target}_ports.txt
```

**Process:**
1. Extract bare hostnames from live hosts list (strip `https://` and `http://` prefixes)
2. **CRITICAL**: naabu requires bare hostnames, NOT URLs — `sed 's|^https://||; s|^http://||'`
3. Run naabu against the clean hostname list
4. Focus investigation on non-standard ports (not 80/443)

**Installation:** `go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest` (installs to `~/go/bin/naabu`)

**Lessons Learned:**
- naabu fails silently with "no valid targets" if input contains URL prefixes
- Cloudflare-proxied hosts typically show ports 80, 443, 8080, 8443 — the 8080/8443 ports are just CF redirects, not real services
- Non-CF hosts (CloudFront, Vercel, direct IPs) are more interesting for port scanning
- SIP port (5060) on CloudFront hosts is usually a false positive

### 8. directory_fuzzing (ffuf)

Brute-force URL paths on live hosts to uncover hidden admin panels, backup files, undocumented API routes, and legacy endpoints.

**Command:**
```bash
ffuf -w ~/SecLists/Discovery/Web-Content/common.txt -u "https://{host}/FUZZ" -mc 200,301,302,403 -t 50 -timeout 5
```

**Process:**
1. Target only hosts that returned 200/301/302 in httpx (skip 403/404 catch-all hosts)
2. Run ffuf per-host, NOT with `FUZZ.{domain}` pattern
3. **IMPORTANT**: Use `-fs {size}` to filter out Cloudflare WAF 403 responses (typically 5453 bytes)
4. Focus on hosts NOT behind Cloudflare for best results (WordPress, Laravel, Docusaurus instances)

**Prerequisites:** SecLists must be installed (`git clone --depth 1 https://github.com/danielmiessler/SecLists.git ~/SecLists`)

**Lessons Learned:**
- Cloudflare WAF returns uniform 403 (5453 bytes) for ALL fuzzing — use `-fs 5453` to filter
- ffuf v2.1.0 does NOT support `-s` (silent) or `-ac` (autocalibrate) flags correctly — omit them
- Target non-CF hosts preferentially: WordPress sites, API endpoints (Laravel), docs sites (Docusaurus)
- `-mc 200,301,302,403` catches everything but adds noise from Cloudflare — consider `-mc 200,301,302` only

### 9. vulnerability_scanning (nuclei)

Run community-maintained templates against live hosts to catch known CVEs, exposed admin panels, default credentials, misconfigured headers, SSRF vectors, and more.

**Command:**
```bash
nuclei -l {target}_live.txt -severity medium,high,critical -timeout 10 -retries 0 -o {target}_vulns.txt
```

**Process:**
1. Feed the full live hosts list from step 6
2. Scan with medium/high/critical severity (skip info/low for speed)
3. Review findings manually — nuclei can produce false positives on Cloudflare-protected hosts

**Lessons Learned:**
- Nuclei uses ~700MB RAM and takes 10-15+ minutes for 60+ hosts with 9000+ templates
- Do NOT use `-bulk-size 50 -c 50` — causes "concurrency higher than max-host-error" warnings
- Hardened targets (full Cloudflare, proper headers) typically yield 0 findings — this is expected
- Run nuclei in background while investigating httpx/naabu results manually

## Output

```json
{
  "skill": "subdomain_enumeration",
  "domain": "string",
  "results": {
    "total_subdomains": "number",
    "subdomains": [
      {
        "fqdn": "api.example.com",
        "source": "crt.sh",
        "resolves": true,
        "ip_addresses": ["array"]
      }
    ],
    "sources_queried": ["crt.sh", "search_dorks", "wordlist"],
    "naming_patterns_detected": [
      {
        "pattern": "{env}-{service}",
        "examples": ["prod-api", "staging-api", "dev-api"]
      }
    ]
  },
  "evidence": [
    {
      "type": "ct_log",
      "source": "crt.sh",
      "count": "number",
      "timestamp": "ISO-8601"
    }
  ]
}
```

## Naming Pattern Detection

Analyze discovered subdomains to detect naming conventions:

```
Pattern: {environment}-{service}
  Examples: prod-api, staging-web, dev-backend

Pattern: {service}.{environment}
  Examples: api.prod, web.staging, backend.dev

Pattern: {service}{number}
  Examples: api1, api2, web01, web02

Pattern: {geo}-{service}
  Examples: us-east-api, eu-west-cdn, apac-app
```

## Rate Limiting

| Source | Rate Limit |
|--------|------------|
| crt.sh | 10 requests/minute |
| Search engines | 10 requests/minute |
| DNS resolution | 30 requests/minute |

## Error Handling

- If crt.sh times out, retry with backoff
- If search engine blocks, wait and retry
- Continue with partial results if some sources fail
- Log all errors for debugging

## Security Considerations

- Only use passive techniques
- No active subdomain brute-forcing
- Respect rate limits to avoid blocking
- Log all queries for audit trail
