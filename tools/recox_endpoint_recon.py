#!/usr/bin/env python3
"""
RecoX Endpoint Recon - Offline script replicating recox.hackerz.space endpoint recon.

Queries Wayback Machine, Common Crawl, AlienVault OTX, and URLScan.io
to discover historical endpoints for a target domain.

Usage:
    python3 recox_endpoint_recon.py example.com
    python3 recox_endpoint_recon.py example.com --sources wayback,otx
    python3 recox_endpoint_recon.py example.com -o custom_output.txt
    python3 recox_endpoint_recon.py example.com --extensions js,json,xml
"""

import argparse
import asyncio
import json
import sys
import time
import urllib.parse
from pathlib import Path

try:
    import aiohttp
except ImportError:
    print("[!] aiohttp required: pip install aiohttp")
    sys.exit(1)

SOURCES = ["wayback", "commoncrawl", "otx", "urlscan"]
TIMEOUT = aiohttp.ClientTimeout(total=30)
USER_AGENT = "Mozilla/5.0 (compatible; RecoX-Endpoint-Recon/1.0)"

# Extension filter for interesting endpoints (default: all)
INTERESTING_EXTENSIONS = {
    "js", "json", "xml", "php", "asp", "aspx", "jsp", "do", "action",
    "cgi", "pl", "py", "rb", "go", "api", "graphql", "wsdl", "yaml",
    "yml", "toml", "conf", "config", "env", "bak", "old", "orig",
    "sql", "db", "log", "txt", "csv", "zip", "tar", "gz",
}


def print_banner(domain: str, sources: list[str]) -> None:
    print(f"\n{'='*60}")
    print(f"  RecoX Endpoint Recon - {domain}")
    print(f"  Sources: {', '.join(sources)}")
    print(f"{'='*60}\n")


async def fetch_wayback(session: aiohttp.ClientSession, domain: str) -> set[str]:
    """Query Wayback Machine CDX API for historical URLs."""
    # Try text output first (more reliable, avoids JSON parse issues on large results)
    url_text = (
        f"https://web.archive.org/cdx/search/cdx"
        f"?url=*.{domain}/*&matchType=domain&output=text"
        f"&collapse=urlkey&fl=original&limit=50000"
    )
    url_json = (
        f"https://web.archive.org/cdx/search/cdx"
        f"?url=*.{domain}/*&matchType=domain&output=json"
        f"&collapse=urlkey&fl=original&limit=50000"
    )
    endpoints = set()
    for attempt, url in enumerate([url_text, url_json], 1):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=90)) as resp:
                if resp.status == 200:
                    if attempt == 1:  # text format
                        text = await resp.text()
                        for line in text.strip().split("\n"):
                            line = line.strip()
                            if line:
                                endpoints.add(line)
                    else:  # json format
                        data = await resp.json(content_type=None)
                        for row in data[1:] if data else []:
                            if row and row[0]:
                                endpoints.add(row[0])
                    if endpoints:
                        break
                elif resp.status == 429:
                    wait = 5 * attempt
                    print(f"  [!] Wayback Machine: rate limited, retrying in {wait}s...")
                    await asyncio.sleep(wait)
                    continue
        except asyncio.TimeoutError:
            print(f"  [!] Wayback Machine: timeout (attempt {attempt})")
        except Exception as e:
            print(f"  [!] Wayback Machine: {e} (attempt {attempt})")
    return endpoints


async def fetch_commoncrawl(session: aiohttp.ClientSession, domain: str) -> set[str]:
    """Query Common Crawl index for URLs."""
    endpoints = set()
    try:
        # Get latest index
        async with session.get(
            "https://index.commoncrawl.org/collinfo.json",
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                print("  [!] Common Crawl: failed to get index list")
                return endpoints
            indexes = await resp.json(content_type=None)

        if not indexes:
            return endpoints

        # Query the 3 most recent indexes in parallel
        latest = [idx["cdx-api"] for idx in indexes[:3]]

        async def query_index(cdx_api: str) -> set[str]:
            results = set()
            params = f"?url=*.{domain}&output=json&limit=10000"
            try:
                async with session.get(
                    cdx_api + params,
                    timeout=aiohttp.ClientTimeout(total=45),
                ) as r:
                    if r.status == 200:
                        text = await r.text()
                        for line in text.strip().split("\n"):
                            if not line:
                                continue
                            try:
                                record = json.loads(line)
                                if "url" in record:
                                    results.add(record["url"])
                            except json.JSONDecodeError:
                                continue
            except (asyncio.TimeoutError, Exception):
                pass
            return results

        tasks = [query_index(api) for api in latest]
        results = await asyncio.gather(*tasks)
        for result_set in results:
            endpoints.update(result_set)

    except asyncio.TimeoutError:
        print("  [!] Common Crawl: timeout")
    except Exception as e:
        print(f"  [!] Common Crawl: {e}")
    return endpoints


async def fetch_otx(session: aiohttp.ClientSession, domain: str) -> set[str]:
    """Query AlienVault OTX for historical URLs."""
    endpoints = set()
    page = 1
    has_next = True
    while has_next and page <= 20:
        url = (
            f"https://otx.alienvault.com/api/v1/indicators/domain"
            f"/{domain}/url_list?limit=200&page={page}"
        )
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    url_list = data.get("url_list", [])
                    for entry in url_list:
                        if "url" in entry:
                            endpoints.add(entry["url"])
                    has_next = data.get("has_next", False)
                    page += 1
                else:
                    has_next = False
        except asyncio.TimeoutError:
            print("  [!] OTX: timeout")
            break
        except Exception as e:
            print(f"  [!] OTX: {e}")
            break
    return endpoints


async def fetch_urlscan(session: aiohttp.ClientSession, domain: str) -> set[str]:
    """Query URLScan.io for historical URLs."""
    url = f"https://urlscan.io/api/v1/search/?q=page.domain:{domain}&size=10000"
    endpoints = set()
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                for result in data.get("results", []):
                    page_url = result.get("page", {}).get("url")
                    if page_url:
                        endpoints.add(page_url)
                    task_url = result.get("task", {}).get("url")
                    if task_url:
                        endpoints.add(task_url)
            elif resp.status == 429:
                print("  [!] URLScan: rate limited (429)")
    except asyncio.TimeoutError:
        print("  [!] URLScan: timeout")
    except Exception as e:
        print(f"  [!] URLScan: {e}")
    return endpoints


SOURCE_FUNCS = {
    "wayback": fetch_wayback,
    "commoncrawl": fetch_commoncrawl,
    "otx": fetch_otx,
    "urlscan": fetch_urlscan,
}


def normalize_url(url: str) -> str:
    """Normalize URL for deduplication."""
    parsed = urllib.parse.urlparse(url)
    # Remove fragment, normalize scheme
    return urllib.parse.urlunparse(
        (parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, parsed.params, parsed.query, "")
    )


def filter_endpoints(
    endpoints: set[str],
    domain: str,
    extensions: set[str] | None = None,
    exclude_media: bool = True,
) -> list[str]:
    """Filter and deduplicate endpoints."""
    media_exts = {"png", "jpg", "jpeg", "gif", "svg", "ico", "webp", "mp4", "mp3", "woff", "woff2", "ttf", "eot", "css"}
    seen = set()
    filtered = []

    for url in endpoints:
        normalized = normalize_url(url)
        if normalized in seen:
            continue

        # Must belong to the target domain
        parsed = urllib.parse.urlparse(normalized)
        if domain not in parsed.netloc:
            continue

        # Exclude media files
        if exclude_media:
            path_lower = parsed.path.lower()
            ext = path_lower.rsplit(".", 1)[-1] if "." in path_lower else ""
            if ext in media_exts:
                continue

        # Extension filter (if specified)
        if extensions:
            path_lower = parsed.path.lower()
            ext = path_lower.rsplit(".", 1)[-1] if "." in path_lower else ""
            if ext and ext not in extensions:
                continue

        seen.add(normalized)
        filtered.append(url)

    return sorted(filtered)


async def run_recon(domain: str, sources: list[str]) -> dict[str, set[str]]:
    """Run all source queries in parallel."""
    headers = {"User-Agent": USER_AGENT}
    results: dict[str, set[str]] = {}

    async with aiohttp.ClientSession(headers=headers, timeout=TIMEOUT) as session:
        tasks = {}
        for source in sources:
            if source in SOURCE_FUNCS:
                tasks[source] = asyncio.create_task(SOURCE_FUNCS[source](session, domain))

        for source, task in tasks.items():
            print(f"  [*] Querying {source}...")

        for source, task in tasks.items():
            try:
                result = await task
                results[source] = result
                print(f"  [+] {source}: {len(result)} endpoints")
            except Exception as e:
                print(f"  [!] {source}: failed ({e})")
                results[source] = set()

    return results


def export_results(
    endpoints: list[str],
    domain: str,
    output_path: str | None,
    source_counts: dict[str, int],
) -> str:
    """Export results to TXT file."""
    if output_path:
        path = Path(output_path)
    else:
        safe_domain = domain.replace(".", "_")
        path = Path(f"{safe_domain}_endpoints.txt")

    with open(path, "w") as f:
        f.write(f"# RecoX Endpoint Recon - {domain}\n")
        f.write(f"# Date: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
        f.write(f"# Total unique endpoints: {len(endpoints)}\n")
        for source, count in source_counts.items():
            f.write(f"# {source}: {count}\n")
        f.write("#\n")
        for ep in endpoints:
            f.write(ep + "\n")

    return str(path)


def main():
    parser = argparse.ArgumentParser(
        description="RecoX Endpoint Recon - discover historical endpoints for a domain"
    )
    parser.add_argument("domain", help="Target domain (e.g., example.com)")
    parser.add_argument(
        "--sources", "-s",
        default=",".join(SOURCES),
        help=f"Comma-separated sources (default: {','.join(SOURCES)})",
    )
    parser.add_argument("--output", "-o", help="Output file path (default: <domain>_endpoints.txt)")
    parser.add_argument(
        "--extensions", "-e",
        help="Filter by extensions (e.g., js,json,xml). Default: all non-media",
    )
    parser.add_argument(
        "--interesting-only", "-i",
        action="store_true",
        help="Show only interesting extensions (js, json, xml, php, asp, config, env, etc.)",
    )
    parser.add_argument(
        "--include-media",
        action="store_true",
        help="Include media files (png, jpg, css, fonts, etc.)",
    )

    args = parser.parse_args()

    # Clean domain
    domain = args.domain.strip().lower()
    domain = domain.replace("https://", "").replace("http://", "").rstrip("/")

    # Parse sources
    sources = [s.strip() for s in args.sources.split(",") if s.strip() in SOURCE_FUNCS]
    if not sources:
        print(f"[!] No valid sources. Available: {', '.join(SOURCES)}")
        sys.exit(1)

    # Parse extension filter
    ext_filter = None
    if args.extensions:
        ext_filter = {e.strip().lower().lstrip(".") for e in args.extensions.split(",")}
    elif args.interesting_only:
        ext_filter = INTERESTING_EXTENSIONS

    print_banner(domain, sources)

    # Run recon
    start = time.time()
    results = asyncio.run(run_recon(domain, sources))
    elapsed = time.time() - start

    # Merge all endpoints
    all_endpoints: set[str] = set()
    source_counts = {}
    for source, eps in results.items():
        all_endpoints.update(eps)
        source_counts[source] = len(eps)

    # Filter and deduplicate
    filtered = filter_endpoints(
        all_endpoints,
        domain,
        extensions=ext_filter,
        exclude_media=not args.include_media,
    )

    # Print summary
    print(f"\n{'='*60}")
    print(f"  Results Summary")
    print(f"{'='*60}")
    print(f"  Total raw:     {len(all_endpoints)}")
    print(f"  After filter:  {len(filtered)}")
    print(f"  Time:          {elapsed:.1f}s")
    for source, count in source_counts.items():
        print(f"  {source:15s} {count:>6d} endpoints")

    if not filtered:
        print("\n  [!] No endpoints found.")
        sys.exit(0)

    # Export
    output_file = export_results(filtered, domain, args.output, source_counts)
    print(f"\n  [+] Saved to: {output_file}")
    print(f"  [+] {len(filtered)} unique endpoints\n")


if __name__ == "__main__":
    main()
