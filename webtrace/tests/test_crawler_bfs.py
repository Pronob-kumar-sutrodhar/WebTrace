"""
Unit tests for WebCrawler BFS traversal logic using mock in-memory HTML pages.
Verifies that:
1. Crawl order is strictly BFS (level-by-level), NOT DFS.
2. The visited Set prevents duplicate visits on cycles and cross-links.
3. Domain boundary restriction is strictly respected.
4. Max depth and max pages limits are respected.
"""

from typing import Dict, Optional
import pytest
from webtrace.crawler import WebCrawler


class MockFetcher:
    """Simulates a web server by serving predefined HTML strings for known URLs."""

    def __init__(self, pages: Dict[str, str]) -> None:
        self.pages = pages
        self.fetch_log: list[str] = []

    def fetch(self, url: str) -> Optional[str]:
        self.fetch_log.append(url)
        return self.pages.get(url, None)


class TestCrawlerBFS:
    """Test suite for BFS crawling algorithm."""

    @pytest.fixture
    def mock_website(self) -> Dict[str, str]:
        """
        Constructs a structured multi-level mock website:
        
        Seed: https://example.com/ (Level 0)
          |--> https://example.com/a (Level 1)
          |      |--> https://example.com/a1 (Level 2)
          |      |--> https://example.com/a2 (Level 2)
          |      |--> https://example.com/ (Cycle back to Seed)
          |
          |--> https://example.com/b (Level 1)
                 |--> https://example.com/b1 (Level 2)
                 |--> https://example.com/a1 (Cross-link to a1)
                 |--> https://external-domain.com/blog (External link)
        """
        return {
            "https://example.com/": """
                <html>
                    <head><title>Home Page</title></head>
                    <body>
                        <a href="/a">Page A</a>
                        <a href="/b">Page B</a>
                    </body>
                </html>
            """,
            "https://example.com/a": """
                <html>
                    <head><title>Page A</title></head>
                    <body>
                        <a href="/a1">Page A1</a>
                        <a href="/a2">Page A2</a>
                        <a href="/">Back to Home</a>
                    </body>
                </html>
            """,
            "https://example.com/b": """
                <html>
                    <head><title>Page B</title></head>
                    <body>
                        <a href="/b1">Page B1</a>
                        <a href="/a1">Link to A1</a>
                        <a href="https://external-domain.com/blog">External Site</a>
                    </body>
                </html>
            """,
            "https://example.com/a1": "<html><head><title>Page A1</title></head><body></body></html>",
            "https://example.com/a2": "<html><head><title>Page A2</title></head><body></body></html>",
            "https://example.com/b1": "<html><head><title>Page B1</title></head><body></body></html>",
        }

    def test_bfs_level_order_traversal(self, mock_website):
        """
        Verifies that nodes are visited strictly level-by-level:
        Level 0: https://example.com/
        Level 1: https://example.com/a, https://example.com/b
        Level 2: https://example.com/a1, https://example.com/a2, https://example.com/b1
        
        If DFS were accidentally used (e.g. stack/recursion), order would be:
        Home -> A -> A1 -> A2 -> B... (DFS)
        """
        fetcher = MockFetcher(mock_website)
        crawler = WebCrawler(
            seed_url="https://example.com/",
            max_depth=2,
            max_pages=20,
            fetcher=fetcher,
            verbose=False,
        )

        crawled_pages, graph = crawler.crawl()
        visited_urls = [page.url for page in crawled_pages]

        # Expected strict BFS order:
        expected_bfs_order = [
            "https://example.com/",    # Depth 0
            "https://example.com/a",    # Depth 1
            "https://example.com/b",    # Depth 1
            "https://example.com/a1",   # Depth 2
            "https://example.com/a2",   # Depth 2
            "https://example.com/b1",   # Depth 2
        ]

        assert visited_urls == expected_bfs_order
        # Confirm that both Level 1 nodes were fetched BEFORE any Level 2 nodes
        assert visited_urls.index("https://example.com/a") < visited_urls.index("https://example.com/a1")
        assert visited_urls.index("https://example.com/b") < visited_urls.index("https://example.com/a1")

    def test_cycle_and_cross_link_deduplication(self, mock_website):
        """Verifies that pages are never fetched more than once despite cycles and cross links."""
        fetcher = MockFetcher(mock_website)
        crawler = WebCrawler(
            seed_url="https://example.com/",
            max_depth=2,
            max_pages=20,
            fetcher=fetcher,
            verbose=False,
        )

        crawled_pages, _ = crawler.crawl()
        urls = [p.url for p in crawled_pages]

        # Each URL must appear exactly once
        assert len(urls) == len(set(urls))
        # Root was linked back from /a, but should only be fetched once
        assert fetcher.fetch_log.count("https://example.com/") == 1
        # /a1 was linked from both /a and /b, but should only be fetched once
        assert fetcher.fetch_log.count("https://example.com/a1") == 1

    def test_external_domain_isolation(self, mock_website):
        """Verifies that off-domain URLs are not visited or added to the crawl."""
        fetcher = MockFetcher(mock_website)
        crawler = WebCrawler(
            seed_url="https://example.com/",
            max_depth=2,
            max_pages=20,
            fetcher=fetcher,
            verbose=False,
        )

        crawled_pages, graph = crawler.crawl()
        visited_urls = [p.url for p in crawled_pages]

        assert "https://external-domain.com/blog" not in visited_urls
        assert "https://external-domain.com/blog" not in graph

    def test_max_depth_constraint(self, mock_website):
        """Verifies that crawling strictly halts at max_depth."""
        fetcher = MockFetcher(mock_website)
        crawler = WebCrawler(
            seed_url="https://example.com/",
            max_depth=1,  # Only level 0 and level 1
            max_pages=20,
            fetcher=fetcher,
            verbose=False,
        )

        crawled_pages, _ = crawler.crawl()
        visited_urls = [p.url for p in crawled_pages]

        # Only depth 0 and depth 1 should be visited
        assert visited_urls == [
            "https://example.com/",
            "https://example.com/a",
            "https://example.com/b",
        ]

    def test_max_pages_constraint(self, mock_website):
        """Verifies that crawl halts when max_pages limit is reached."""
        fetcher = MockFetcher(mock_website)
        crawler = WebCrawler(
            seed_url="https://example.com/",
            max_depth=5,
            max_pages=3,  # Cap at 3 pages
            fetcher=fetcher,
            verbose=False,
        )

        crawled_pages, _ = crawler.crawl()
        assert len(crawled_pages) == 3
