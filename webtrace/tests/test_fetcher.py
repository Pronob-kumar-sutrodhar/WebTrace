"""
Unit tests for Fetcher module: HTTP fetching, robots.txt parsing, politeness delay,
and error handling.
"""

import time
from unittest.mock import MagicMock, patch
import pytest
import requests
from webtrace.fetcher import Fetcher, DEFAULT_USER_AGENT


class TestFetcher:
    """Test suite for HTTP Fetcher component."""

    def test_custom_user_agent_header(self):
        custom_ua = "CustomWebTraceBot/2.0 (Testing)"
        fetcher = Fetcher(user_agent=custom_ua, delay=0.0)
        assert fetcher.session.headers.get("User-Agent") == custom_ua

    def test_fetch_successful_html(self):
        fetcher = Fetcher(delay=0.0, respect_robots=False)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_resp.text = "<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>"

        with patch.object(fetcher.session, "get", return_value=mock_resp):
            content = fetcher.fetch("https://example.com/page")
            assert content == mock_resp.text

    def test_fetch_non_html_ignored(self):
        # PDFs or images should return None rather than being parsed as HTML
        fetcher = Fetcher(delay=0.0, respect_robots=False)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "application/pdf"}
        mock_resp.text = "%PDF-1.4 binary data..."

        with patch.object(fetcher.session, "get", return_value=mock_resp):
            content = fetcher.fetch("https://example.com/file.pdf")
            assert content is None

    def test_fetch_http_error_handling(self):
        # 404 Not Found, 500 Internal Error, etc. should return None gracefully
        fetcher = Fetcher(delay=0.0, respect_robots=False)

        mock_resp = MagicMock()
        mock_resp.status_code = 404

        with patch.object(fetcher.session, "get", return_value=mock_resp):
            assert fetcher.fetch("https://example.com/notfound") is None

        # Network timeouts/connection errors should also return None without crashing
        with patch.object(fetcher.session, "get", side_effect=requests.exceptions.Timeout):
            assert fetcher.fetch("https://example.com/timeout") is None

    def test_robots_txt_disallowed_and_allowed(self):
        fetcher = Fetcher(delay=0.0, respect_robots=True)

        robots_content = """
User-agent: *
Disallow: /private/
Disallow: /admin/
Allow: /public/
"""
        mock_robots_resp = MagicMock()
        mock_robots_resp.status_code = 200
        mock_robots_resp.text = robots_content

        mock_page_resp = MagicMock()
        mock_page_resp.status_code = 200
        mock_page_resp.headers = {"Content-Type": "text/html"}
        mock_page_resp.text = "<html><body>Public Page</body></html>"

        def mock_get(url, *args, **kwargs):
            if url.endswith("/robots.txt"):
                return mock_robots_resp
            return mock_page_resp

        with patch.object(fetcher.session, "get", side_effect=mock_get):
            # Allowed paths
            assert fetcher.can_fetch("https://example.com/public/page") is True
            assert fetcher.can_fetch("https://example.com/about") is True
            assert fetcher.fetch("https://example.com/about") == "<html><body>Public Page</body></html>"

            # Disallowed paths
            assert fetcher.can_fetch("https://example.com/private/secret") is False
            assert fetcher.can_fetch("https://example.com/admin/dashboard") is False
            assert fetcher.fetch("https://example.com/private/secret") is None

    def test_politeness_delay_enforcement(self):
        delay_duration = 0.2  # 200 ms
        fetcher = Fetcher(delay=delay_duration, respect_robots=False)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "text/html"}
        mock_resp.text = "<html><body>Page</body></html>"

        with patch.object(fetcher.session, "get", return_value=mock_resp):
            start = time.time()
            fetcher.fetch("https://example.com/page1")
            fetcher.fetch("https://example.com/page2")
            elapsed = time.time() - start

            # Second request must have waited for the delay duration
            assert elapsed >= (delay_duration - 0.05)
