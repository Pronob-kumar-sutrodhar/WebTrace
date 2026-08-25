"""
================================================================================
WebTrace: Network Fetcher, Robots.txt Compliance & Politeness Module
================================================================================
DSA Concept Demonstrated:
- Hash Map (dict) Caching for O(1) Per-Domain Metadata & Rate-Limiting.

Why this matters for Web Crawler Engineering:
1. robots.txt Caching:
   - Every domain publishes crawl rules at '/robots.txt'. To avoid making redundant
     network calls for robots.txt before visiting each page, we cache the parsed
     RobotFileParser instance in a Hash Map (`_robots_cache: dict[str, RobotFileParser]`).
   - This ensures O(1) average lookup time when verifying whether a URL is crawlable.

2. Politeness Delay & Domain State Tracking:
   - Web crawlers must never overwhelm target web servers. We track the timestamp
     of the most recent request per domain in a Hash Map (`_last_request_time: dict[str, float]`)
     to calculate and enforce a mandatory polite interval (e.g., 1.0s delay).
================================================================================
"""

import logging
import time
from typing import Dict, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import requests

from webtrace.url_utils import get_domain_key

logger = logging.getLogger("webtrace.fetcher")

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 WebTrace/1.0"


class Fetcher:
    """
    Handles robust HTTP GET requests with custom User-Agent identification,
    robots.txt policy verification, and domain-specific politeness rate-limiting.
    """

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: float = 5.0,
        delay: float = 1.0,
        respect_robots: bool = True,
    ) -> None:
        """
        Initializes the fetcher.

        Args:
            user_agent: Descriptive User-Agent header string.
            timeout: Maximum seconds to wait for network responses.
            delay: Politeness delay (in seconds) between requests to the same domain.
            respect_robots: Whether to check and enforce robots.txt rules.
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.delay = delay
        self.respect_robots = respect_robots

        # Configure persistent HTTP session with standard headers
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

        # Hash Maps for O(1) caching and state tracking
        self._robots_cache: Dict[str, Optional[RobotFileParser]] = {}
        self._last_request_time: Dict[str, float] = {}

    def _get_domain_root(self, url: str) -> str:
        """Extracts the root origin (e.g. 'https://example.com') from a URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def get_robots_parser(self, url: str) -> Optional[RobotFileParser]:
        """
        Retrieves or downloads and parses the robots.txt file for the given URL's domain.
        Results are cached in self._robots_cache for O(1) subsequent lookups.
        """
        if not self.respect_robots:
            return None

        domain_root = self._get_domain_root(url)
        if domain_root in self._robots_cache:
            return self._robots_cache[domain_root]

        robots_url = f"{domain_root}/robots.txt"
        rp = RobotFileParser()

        try:
            logger.debug(f"Fetching robots.txt: {robots_url}")
            resp = self.session.get(robots_url, timeout=self.timeout)
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
                self._robots_cache[domain_root] = rp
                logger.debug(f"Parsed and cached robots.txt for {domain_root}")
            elif resp.status_code in (401, 403):
                logger.warning(f"robots.txt returned HTTP {resp.status_code} for {domain_root}; access disallowed")
                rp.disallow_all = True
                self._robots_cache[domain_root] = rp
            else:
                logger.debug(f"robots.txt returned HTTP {resp.status_code} for {domain_root}; access allowed by default")
                rp.allow_all = True
                self._robots_cache[domain_root] = rp
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt for {domain_root}: {e}; allowing by default")
            rp.allow_all = True
            self._robots_cache[domain_root] = rp

        return self._robots_cache[domain_root]

    def can_fetch(self, url: str) -> bool:
        """
        Checks whether robots.txt permits crawling the given URL.
        """
        if not self.respect_robots:
            return True

        rp = self.get_robots_parser(url)
        if rp is None:
            return True

        allowed = rp.can_fetch(self.user_agent, url)
        if not allowed:
            allowed = rp.can_fetch("*", url)

        if not allowed:
            logger.warning(f"Access disallowed by robots.txt: {url}")

        return allowed

    def _apply_politeness_delay(self, url: str) -> None:
        """
        Enforces a polite waiting interval between requests targeting the same domain.
        """
        if self.delay <= 0:
            return

        domain_key = get_domain_key(url)
        now = time.time()
        last_time = self._last_request_time.get(domain_key, 0.0)
        elapsed = now - last_time

        if elapsed < self.delay:
            wait_time = self.delay - elapsed
            logger.debug(f"Politeness delay: sleeping for {wait_time:.2f}s before fetching {url}")
            time.sleep(wait_time)

        self._last_request_time[domain_key] = time.time()

    def fetch(self, url: str) -> Optional[str]:
        """
        Fetches the HTML content of a URL while respecting robots.txt and politeness.

        Returns:
            HTML string if successfully downloaded (HTTP 200 and text/html),
            or None if disallowed, failed, timed out, or non-HTML.
        """
        # Step 1: Verify robots.txt permissions
        if not self.can_fetch(url):
            return None

        # Step 2: Enforce politeness delay
        self._apply_politeness_delay(url)

        # Step 3: Perform HTTP GET request
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} error fetching {url}")
                return None

            # Verify response is HTML
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                logger.warning(f"Skipping non-HTML content-type '{content_type}' for {url}")
                return None

            logger.info(f"Fetched: {url} (HTTP 200, {len(response.text)} bytes)")
            return response.text

        except requests.RequestException as exc:
            logger.warning(f"Network error fetching {url}: {exc}")
            return None
