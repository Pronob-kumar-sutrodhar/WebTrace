"""
================================================================================
WebTrace: Interactive Terminal UI
================================================================================
Prompts the user directly in the console for crawl inputs (URL, Depth, Pages),
executes the Breadth-First Search crawl, and displays a formatted table of
the collected data right in the terminal.

Usage:
    python -m webtrace.interactive
    or
    python webtrace/interactive.py
================================================================================
"""

import os
import sys
import time

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from webtrace.crawler import WebCrawler
from webtrace.exporter import export_all
from webtrace.fetcher import Fetcher
from webtrace.url_utils import normalize_url


def prompt_user_inputs():
    print("=" * 75)
    print("  WebTrace: Interactive Console Interface")
    print("  Domain-Restricted BFS Web Crawler (DSA Course Project)")
    print("=" * 75)

    # 1. URL Input
    while True:
        raw_url = input("\n[?] Enter Target Seed URL (e.g. https://example.com/): ").strip()
        if not raw_url:
            raw_url = "https://example.com/"
            print(f"    (Defaulting to: {raw_url})")

        canonical_url = normalize_url(raw_url)
        if canonical_url:
            break
        print("    [!] Invalid URL. Please ensure it starts with http:// or https://")

    # 2. Max Depth Input
    raw_depth = input("[?] Enter Maximum BFS Crawl Depth [default 2]: ").strip()
    try:
        max_depth = int(raw_depth) if raw_depth else 2
    except ValueError:
        max_depth = 2
        print("    (Invalid number; defaulting to 2)")

    # 3. Max Pages Input
    raw_pages = input("[?] Enter Maximum Pages to Crawl [default 10]: ").strip()
    try:
        max_pages = int(raw_pages) if raw_pages else 10
    except ValueError:
        max_pages = 10
        print("    (Invalid number; defaulting to 10)")

    # 4. Politeness Delay
    raw_delay = input("[?] Enter Politeness Delay in seconds [default 0.5]: ").strip()
    try:
        delay = float(raw_delay) if raw_delay else 0.5
    except ValueError:
        delay = 0.5
        print("    (Invalid number; defaulting to 0.5s)")

    return canonical_url, max_depth, max_pages, delay


def display_collected_table(crawled_pages, graph, elapsed_time):
    print("\n" + "=" * 95)
    print("                        COLLECTED CRAWL DATA (BFS TREE TABLE)")
    print("=" * 95)
    print(f"{'#':<3} | {'Depth':<5} | {'Title':<25} | {'Outgoing':<8} | {'URL'}")
    print("-" * 95)

    if not crawled_pages:
        print("No pages were collected (target site was unreachable or blocked).")
    else:
        for idx, page in enumerate(crawled_pages, start=1):
            short_title = (page.title[:22] + "...") if len(page.title) > 25 else page.title
            print(f"{idx:<3} | Lvl {page.depth:<2} | {short_title:<25} | {page.outgoing_count:<8} | {page.url}")

    print("=" * 95)
    print(f"[*] Crawl Summary: {len(crawled_pages)} pages crawled | {graph.node_count} nodes | {graph.edge_count} directed edges | Time: {elapsed_time:.2f}s")
    print("=" * 95)


def main():
    seed_url, max_depth, max_pages, delay = prompt_user_inputs()

    print("\n[*] Initializing BFS crawl...")
    fetcher = Fetcher(delay=delay, timeout=5.0, respect_robots=True)
    crawler = WebCrawler(
        seed_url=seed_url,
        max_depth=max_depth,
        max_pages=max_pages,
        fetcher=fetcher,
        verbose=True,
    )

    start = time.time()
    crawled_pages, graph = crawler.crawl()
    elapsed = time.time() - start

    # Display collected data in console
    display_collected_table(crawled_pages, graph, elapsed)

    # Save exports
    output_dir = os.path.join(CURRENT_DIR, "output")
    csv_file, json_file = export_all(crawled_pages, graph, output_dir=output_dir)
    print(f"\n[+] Results saved:")
    print(f"    - CSV:  {csv_file}")
    print(f"    - JSON: {json_file}\n")


if __name__ == "__main__":
    main()
