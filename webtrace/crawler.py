"""
================================================================================
WebTrace: Main Crawler Controller (Breadth-First Search Traversal)
================================================================================
DSA Concepts Demonstrated:
1. Queue (FIFO - collections.deque):
   - Controls the exploration frontier. URLs are enqueued at the back (append)
     and dequeued from the front (popleft).
   - This FIFO (First-In, First-Out) discipline guarantees Breadth-First Search (BFS)
     order: all pages at depth d are visited before any page at depth d + 1.

2. Hash Set (set):
   - Stores the 'visited' (discovered) URLs.
   - Provides O(1) average-time complexity for membership lookups ("if url in visited:").
   - Crucial for preventing infinite cycles caused by cyclic hyperlinks (e.g. A -> B -> A)
     and eliminating redundant page fetches.

3. Graph (LinkGraph - Adjacency List):
   - Stores the website's topology as pages (vertices) and hyperlinks (directed edges).

4. Breadth-First Search (BFS) Algorithm:
   - Level-by-level traversal outward from the seed URL.
   - Guarantees discovering the shortest path (in terms of clicks/hops) from
     the seed URL to every reachable page.
================================================================================
"""

from collections import deque
from dataclasses import dataclass, field
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from webtrace.fetcher import Fetcher
from webtrace.graph import LinkGraph
from webtrace.parser import extract_comprehensive_page_data
from webtrace.url_utils import is_same_domain, normalize_url

logger = logging.getLogger("webtrace.crawler")


@dataclass
class CrawlTask:
    """Represents a URL pending exploration in the BFS Queue."""
    url: str
    depth: int
    parent_url: Optional[str] = None


@dataclass
class CrawledPage:
    """Stores metadata and comprehensive extracted content of a successfully visited page."""
    url: str
    title: str
    depth: int
    parent_url: Optional[str]
    outgoing_links: List[str] = field(default_factory=list)
    snippet: str = ""
    text_blocks: List[str] = field(default_factory=list)
    documents: List[Dict[str, str]] = field(default_factory=list)
    all_urls: List[str] = field(default_factory=list)
    extracted_data: List[str] = field(default_factory=list)

    @property
    def outgoing_count(self) -> int:
        return len(self.outgoing_links)


class WebCrawler:
    """
    Core Domain-Restricted BFS Crawler Engine.
    """

    def __init__(
        self,
        seed_url: str,
        max_depth: int = 2,
        max_pages: int = 50,
        fetcher: Optional[Any] = None,
        link_extractor: Optional[Callable] = None,
        verbose: bool = True,
    ) -> None:
        self.raw_seed_url = seed_url
        self.seed_url = normalize_url(seed_url) or seed_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.fetcher = fetcher if fetcher is not None else Fetcher()
        self.link_extractor = link_extractor or extract_comprehensive_page_data
        self.verbose = verbose

        # ----------------------------------------------------------------------
        # DSA Structures:
        # 1. Queue: Holds pending CrawlTasks (FIFO order ensures BFS)
        # 2. Set: Tracks all discovered URLs for O(1) duplicate prevention
        # 3. LinkGraph: Adjacency list storing the website's directed graph
        # ----------------------------------------------------------------------
        self.queue: deque[CrawlTask] = deque()
        self.visited: Set[str] = set()
        self.graph: LinkGraph = LinkGraph()
        self.crawled_pages: List[CrawledPage] = []

    def crawl(self) -> Tuple[List[CrawledPage], LinkGraph]:
        """
        Executes the main Breadth-First Search (BFS) crawl loop.
        """
        if not self.seed_url:
            logger.error("Invalid seed URL provided. Aborting crawl.")
            return [], self.graph

        # Initialize BFS: Enqueue seed and add to visited set
        self.queue.append(CrawlTask(url=self.seed_url, depth=0, parent_url=None))
        self.visited.add(self.seed_url)
        self.graph.add_node(self.seed_url)

        logger.info(f"Starting BFS crawl from seed: {self.seed_url}")
        logger.info(f"Crawl limits: max_depth={self.max_depth}, max_pages={self.max_pages}")

        # Main BFS Loop
        while self.queue and len(self.crawled_pages) < self.max_pages:
            # FIFO Dequeue: Always remove from front of queue to maintain BFS level order
            current_task = self.queue.popleft()
            current_url = current_task.url
            current_depth = current_task.depth
            parent_url = current_task.parent_url

            # Depth limit boundary check
            if current_depth > self.max_depth:
                logger.debug(f"Skipping {current_url} (depth {current_depth} > max_depth {self.max_depth})")
                continue

            logger.info(
                f"[BFS Step {len(self.crawled_pages) + 1}/{self.max_pages}] Visiting (Depth {current_depth}): {current_url}"
            )

            # Fetch page HTML
            html: Optional[str] = None
            if self.fetcher is not None:
                if hasattr(self.fetcher, "fetch"):
                    html = self.fetcher.fetch(current_url)
                elif callable(self.fetcher):
                    html = self.fetcher(current_url)

            # Handle fetch failure (broken links, timeouts, disallowed by robots.txt)
            if html is None:
                logger.warning(f"Could not retrieve HTML content for: {current_url}")
                continue

            # Parse HTML content (extract title, links, text blocks, documents, and all URLs)
            try:
                parsed_res = self.link_extractor(html, base_url=current_url)
            except TypeError:
                parsed_res = self.link_extractor(html)

            if isinstance(parsed_res, tuple) and len(parsed_res) == 6:
                title, raw_links, snippet, text_blocks, documents, all_urls = parsed_res
            elif isinstance(parsed_res, tuple) and len(parsed_res) == 4:
                title, raw_links, snippet, text_blocks = parsed_res
                documents, all_urls = [], []
            else:
                title, raw_links = parsed_res
                snippet, text_blocks, documents, all_urls = "", [], [], []

            # Filter, normalize, and collect domain-internal outgoing links
            normalized_internal_links: List[str] = []

            for raw_link in raw_links:
                norm_link = normalize_url(raw_link, base_url=current_url)
                if not norm_link:
                    continue

                # Enforce domain restriction (filter out external websites)
                if not is_same_domain(norm_link, self.seed_url):
                    continue

                # Add directed edge in graph: current_url -> norm_link
                self.graph.add_edge(current_url, norm_link)
                normalized_internal_links.append(norm_link)

                # Check Visited Set (O(1) average lookup)
                if norm_link not in self.visited:
                    # Mark as visited IMMEDIATELY upon discovery to prevent duplicate enqueuing
                    self.visited.add(norm_link)
                    # FIFO Enqueue: Add to back of queue
                    self.queue.append(
                        CrawlTask(url=norm_link, depth=current_depth + 1, parent_url=current_url)
                    )

            # Record page visit data
            crawled_record = CrawledPage(
                url=current_url,
                title=title,
                depth=current_depth,
                parent_url=parent_url,
                outgoing_links=normalized_internal_links,
                snippet=snippet,
                text_blocks=text_blocks,
                documents=documents,
                all_urls=all_urls,
                extracted_data=text_blocks,  # backward compatibility
            )
            self.crawled_pages.append(crawled_record)

        logger.info(f"Crawl finished. Total pages visited: {len(self.crawled_pages)}")
        return self.crawled_pages, self.graph
