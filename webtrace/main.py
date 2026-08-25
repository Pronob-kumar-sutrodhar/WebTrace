"""
================================================================================
WebTrace: CLI Application Entry Point
================================================================================
A domain-restricted, BFS-based web crawler built as a teaching artifact
for Data Structures and Algorithms (DSA - ECE 2103).

Usage Examples:
    python -m webtrace.main --seed https://example.com/ --max-depth 2 --max-pages 10
    python -m webtrace.main --seed https://example.com/ --dry-run
    python -m webtrace.main --seed https://example.com/ --verbose
================================================================================
"""

import argparse
import logging
import os
import sys
import time
from typing import List, Tuple

# Ensure project root is in sys.path so direct script execution
# (e.g. `python main.py` from inside webtrace/ folder) works out-of-the-box.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from webtrace.crawler import CrawledPage, WebCrawler
from webtrace.exporter import export_all
from webtrace.fetcher import Fetcher
from webtrace.graph import LinkGraph
from webtrace.url_utils import normalize_url


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configures application logging with clean, informative formatting."""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    # Custom formatter for clean console logs
    formatter = logging.Formatter(
        fmt="[%(levelname)s] %(message)s",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    root_logger = logging.getLogger("webtrace")
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="WebTrace",
        description="Domain-Restricted BFS Web Crawler (DSA Course Project)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--seed",
        type=str,
        default="https://example.com/",
        help="Starting seed URL for the crawl (must include scheme, e.g. https://...)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Maximum crawl depth (distance in hops from the seed page)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Maximum total number of unique pages to crawl",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Politeness delay (seconds) between successive requests to the same domain",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Network request timeout in seconds",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "output"),
        help="Directory where crawled_pages.csv and link_graph.json will be saved",
    )
    parser.add_argument(
        "--no-robots",
        action="store_true",
        help="Disable robots.txt compliance checking (not recommended for live crawls)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the crawl initialization and URL normalization without making network requests",
    )
    parser.add_argument(
        "--web",
        "--gui",
        action="store_true",
        help="Launch the interactive Web Dashboard in your browser",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive terminal prompt mode",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed DEBUG logging (shows robots.txt caching, rate-limit sleep, skipped links)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational console output, only printing critical errors",
    )

    return parser.parse_args()


def print_banner() -> None:
    print("=" * 75)
    print("  WebTrace: Domain-Restricted BFS Web Crawler")
    print("  Course: ECE 2103 - Data Structures & Algorithms")
    print("=" * 75)


def run_crawler(args: argparse.Namespace) -> Tuple[List[CrawledPage], LinkGraph]:
    setup_logging(verbose=args.verbose, quiet=args.quiet)
    logger = logging.getLogger("webtrace.main")

    canonical_seed = normalize_url(args.seed)
    if not canonical_seed:
        logger.error(f"Invalid seed URL provided: '{args.seed}'")
        print("Please provide a valid HTTP/HTTPS URL (e.g. https://example.com/)", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Seed URL        : {canonical_seed}")
    print(f"[*] Max Depth       : {args.max_depth}")
    print(f"[*] Max Pages       : {args.max_pages}")
    print(f"[*] Politeness Delay: {args.delay}s")
    print(f"[*] Respect Robots  : {not args.no_robots}")
    print(f"[*] Output Dir      : {args.output_dir}")
    print(f"[*] Dry-Run Mode    : {args.dry_run}")
    print("-" * 75)

    if args.dry_run:
        print("[Dry-Run] Initializing BFS data structures in dry-run mode...")
        print(f"[Dry-Run] Seed URL normalized successfully -> '{canonical_seed}'")
        print(f"[Dry-Run] Initialized FIFO Queue (collections.deque) with seed node at depth 0.")
        print(f"[Dry-Run] Initialized Visited Set with seed URL for O(1) duplicate protection.")
        print(f"[Dry-Run] Initialized LinkGraph Adjacency List with root vertex.")
        print(f"[Dry-Run] Simulation complete. No network requests dispatched.")
        print("=" * 75)
        graph = LinkGraph()
        graph.add_node(canonical_seed)
        return [], graph

    fetcher = Fetcher(
        timeout=args.timeout,
        delay=args.delay,
        respect_robots=not args.no_robots,
    )

    crawler = WebCrawler(
        seed_url=canonical_seed,
        max_depth=args.max_depth,
        max_pages=args.max_pages,
        fetcher=fetcher,
        verbose=not args.quiet,
    )

    start_time = time.time()
    crawled_pages, graph = crawler.crawl()
    elapsed = time.time() - start_time

    print("-" * 75)
    print(f"[*] Crawl completed in {elapsed:.2f} seconds.")
    print(f"[*] Total Pages Crawled (|V| visited) : {len(crawled_pages)}")
    print(f"[*] Total Discovered Graph Vertices   : {graph.node_count}")
    print(f"[*] Total Discovered Graph Edges (|E|): {graph.edge_count}")
    print("-" * 75)

    # Export results
    csv_file, json_file = export_all(crawled_pages, graph, output_dir=args.output_dir)
    print(f"[+] Crawled Pages CSV exported to: {csv_file}")
    print(f"[+] Link Graph JSON exported to  : {json_file}")
    print("=" * 75)

    return crawled_pages, graph


def main() -> None:
    args = parse_args()
    if args.web:
        from webtrace.app import run_app
        run_app()
        return

    if args.interactive:
        from webtrace.interactive import main as run_interactive
        run_interactive()
        return

    print_banner()
    run_crawler(args)


if __name__ == "__main__":
    main()
