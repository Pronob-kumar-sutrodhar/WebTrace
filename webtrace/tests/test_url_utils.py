"""
Unit tests for URL normalization and domain restriction utilities in WebTrace.
Tests verify handling of tricky edge cases: relative paths, fragment stripping,
casing, trailing slashes, and www vs non-www domain matching.
"""

import pytest
from webtrace.url_utils import normalize_url, is_same_domain, get_domain_key


class TestNormalizeUrl:
    """Test suite for URL canonicalization / normalization."""

    def test_relative_path_resolution(self):
        base = "https://example.com/blog/article1"
        assert normalize_url("/about", base) == "https://example.com/about"
        assert normalize_url("page2", base) == "https://example.com/blog/page2"
        assert normalize_url("../contact", base) == "https://example.com/contact"
        assert normalize_url("./post", base) == "https://example.com/blog/post"

    def test_fragment_stripping(self):
        # Section anchors point to the same page; must strip fragments to prevent duplicate nodes
        base = "https://example.com"
        assert normalize_url("https://example.com/page#section-1", base) == "https://example.com/page"
        assert normalize_url("/docs#installation", base) == "https://example.com/docs"
        assert normalize_url("#top", "https://example.com/home") == "https://example.com/home"

    def test_case_normalization(self):
        # RFC 3986: Scheme and host are case-insensitive
        assert normalize_url("HTTP://EXAMPLE.COM/Page") == "http://example.com/Page"
        assert normalize_url("HTTPS://Www.Example.Com:443/Path") == "https://www.example.com/Path"

    def test_trailing_slash_standardization(self):
        # Root URL gets standardized to '/'
        assert normalize_url("https://example.com") == "https://example.com/"
        assert normalize_url("https://example.com/") == "https://example.com/"
        
        # Subpaths are standardized without trailing slash
        assert normalize_url("https://example.com/about/") == "https://example.com/about"
        assert normalize_url("https://example.com/about") == "https://example.com/about"

    def test_default_port_stripping(self):
        # Standard ports 80 (HTTP) and 443 (HTTPS) should be removed
        assert normalize_url("http://example.com:80/home") == "http://example.com/home"
        assert normalize_url("https://example.com:443/home") == "https://example.com/home"
        # Non-standard ports must be preserved
        assert normalize_url("http://example.com:8080/home") == "http://example.com:8080/home"

    def test_duplicate_slashes_cleaning(self):
        assert normalize_url("https://example.com//a///b//c") == "https://example.com/a/b/c"

    def test_invalid_and_non_http_schemes(self):
        # Non-crawlable URLs should normalize to None
        assert normalize_url("javascript:void(0)") is None
        assert normalize_url("mailto:test@example.com") is None
        assert normalize_url("tel:+1234567890") is None
        assert normalize_url("ftp://files.example.com/doc.pdf") is None
        assert normalize_url("") is None
        assert normalize_url(None) is None


class TestIsSameDomain:
    """Test suite for domain restriction boundary checks."""

    def test_exact_domain_match(self):
        seed = "https://example.com/"
        assert is_same_domain("https://example.com/about", seed) is True
        assert is_same_domain("http://example.com/blog/1", seed) is True

    def test_www_and_non_www_tolerance(self):
        # www.example.com and example.com should be treated as the same domain
        assert is_same_domain("https://www.example.com/news", "https://example.com") is True
        assert is_same_domain("https://example.com/news", "https://www.example.com") is True

    def test_off_domain_rejection(self):
        seed = "https://example.com"
        assert is_same_domain("https://otherdomain.org/about", seed) is False
        assert is_same_domain("https://google.com", seed) is False
        assert is_same_domain("https://example.org", seed) is False

    def test_subdomain_handling(self):
        seed = "https://example.com"
        # Different subdomains (e.g. blog.example.com vs example.com)
        assert is_same_domain("https://blog.example.com", seed) is False

    def test_empty_or_malformed_inputs(self):
        assert is_same_domain("", "https://example.com") is False
        assert is_same_domain("https://example.com", "") is False
        assert is_same_domain(None, "https://example.com") is False
