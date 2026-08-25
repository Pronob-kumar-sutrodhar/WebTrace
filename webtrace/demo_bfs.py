"""
Demonstration script for Phase 2: Simulating BFS web crawl with Mock Fetcher.
This script demonstrates that the crawler visits pages strictly in Breadth-First (level-by-level)
order rather than Depth-First order.
"""

import os
import sys

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from webtrace.crawler import WebCrawler


class MockFetcher:
    """Mock web server providing synthetic HTML pages."""
    def __init__(self, pages: dict[str, str]) -> None:
        self.pages = pages

    def fetch(self, url: str) -> str | None:
        return self.pages.get(url, None)


def run_bfs_demo():
    mock_pages = {
        "https://example.com/": """
            <html>
                <head><title>Home (Depth 0)</title></head>
                <body>
                    <a href="/about">About Us (Depth 1)</a>
                    <a href="/products">Products (Depth 1)</a>
                    <a href="/contact">Contact (Depth 1)</a>
                </body>
            </html>
        """,
        "https://example.com/about": """
            <html>
                <head><title>About Us (Depth 1)</title></head>
                <body>
                    <a href="/about/team">Our Team (Depth 2)</a>
                    <a href="/about/history">Company History (Depth 2)</a>
                    <a href="/">Back to Home (Cycle)</a>
                </body>
            </html>
        """,
        "https://example.com/products": """
            <html>
                <head><title>Products (Depth 1)</title></head>
                <body>
                    <a href="/products/software">Software Catalog (Depth 2)</a>
                    <a href="/about/team">Team Link (Cross Link)</a>
                </body>
            </html>
        """,
        "https://example.com/contact": "<html><head><title>Contact (Depth 1)</title></head><body></body></html>",
        "https://example.com/about/team": "<html><head><title>Team (Depth 2)</title></head><body></body></html>",
        "https://example.com/about/history": "<html><head><title>History (Depth 2)</title></head><body></body></html>",
        "https://example.com/products/software": "<html><head><title>Software (Depth 2)</title></head><body></body></html>",
    }

    print("=" * 70)
    print("WebTrace BFS Crawl Simulation (Mock In-Memory HTML)")
    print("=" * 70)

    fetcher = MockFetcher(mock_pages)
    crawler = WebCrawler(
        seed_url="https://example.com/",
        max_depth=2,
        max_pages=15,
        fetcher=fetcher,
        verbose=True,
    )

    crawled, graph = crawler.crawl()

    print("\n" + "=" * 70)
    print("CRAWL RESULTS SUMMARY:")
    print("=" * 70)
    print(f"{'Order':<6} | {'Depth':<5} | {'Title':<25} | {'URL'}")
    print("-" * 70)
    for idx, page in enumerate(crawled, start=1):
        print(f"{idx:<6} | {page.depth:<5} | {page.title:<25} | {page.url}")

    print("\n" + "=" * 70)
    print("DISCOVERED LINK GRAPH (Adjacency List):")
    print("=" * 70)
    for node, edges in graph.to_dict().items():
        print(f"Node: {node}")
        for edge in edges:
            print(f"  +--> {edge}")


if __name__ == "__main__":
    run_bfs_demo()
