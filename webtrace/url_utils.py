"""
================================================================================
WebTrace: URL Utility & Domain Normalization Module
================================================================================
DSA Concept Demonstrated:
- String Parsing, Canonical Representations, and Set Invariant Maintenance.

Why this matters for Data Structures & Graph Traversal:
In graph theory and algorithms (such as BFS), vertices are uniquely identified.
On the web, a single resource (vertex) can be referenced via many syntactically
distinct URLs (e.g., relative paths '../about', trailing slashes, fragments '#top',
or uppercase schemes 'HTTP://EXAMPLE.COM/').

Without canonical normalization, our Visited Set (Hash Set) would store duplicate
references for the same logical node, breaking the O(1) deduplication invariant,
causing duplicate vertex exploration, and potentially creating infinite crawl cycles.
This module ensures every URL is converted into a canonical form before being
queried or inserted into Hash Sets and Graph adjacency lists.
================================================================================
"""

import re
from urllib.parse import urljoin, urlparse, urlunparse, urldefrag


def get_domain_key(url_or_domain: str) -> str:
    """
    Extracts a normalized domain key from a URL or raw domain name.
    
    Strips leading 'www.' and lowercases the domain to allow seamless matching
    between 'example.com' and 'www.example.com'.
    
    Args:
        url_or_domain: A full URL (e.g. 'https://www.example.com/page') or host string.
        
    Returns:
        A canonical domain string (e.g. 'example.com').
    """
    if "://" in url_or_domain:
        parsed = urlparse(url_or_domain)
        host = parsed.hostname or parsed.netloc or ""
    else:
        # Might be a raw host or host:port
        host = urlparse(f"http://{url_or_domain}").hostname or url_or_domain

    host = host.strip().lower()
    # Strip port if present
    if ":" in host:
        host = host.split(":", 1)[0]
    # Strip leading 'www.' for relaxed domain matching
    if host.startswith("www."):
        host = host[4:]
    return host


def is_same_domain(url: str, seed_url: str) -> bool:
    """
    Determines whether a candidate URL belongs to the same domain as the seed URL.
    
    This enforces the 'domain-restricted' boundary condition of the crawler,
    ensuring graph exploration remains strictly within the subgraph of the target site.
    
    Args:
        url: The candidate URL to check.
        seed_url: The starting/seed URL defining the domain scope.
        
    Returns:
        True if both URLs belong to the same domain (ignoring 'www.'), False otherwise.
    """
    if not url or not seed_url:
        return False

    candidate_domain = get_domain_key(url)
    seed_domain = get_domain_key(seed_url)

    if not candidate_domain or not seed_domain:
        return False

    # Exact match on domain key (e.g., example.com == example.com)
    return candidate_domain == seed_domain


def normalize_url(url: str, base_url: str = "") -> str | None:
    """
    Normalizes a given URL into a canonical string representation.
    
    Steps performed:
    1. Resolve relative URLs against `base_url` (e.g. '/about' -> 'http://example.com/about').
    2. Strip URL fragments (e.g. '#section' is stripped because it points to the same document).
    3. Validate supported schemes (only 'http' and 'https' are crawled; ignores mailto, javascript, tel, etc.).
    4. Lowercase scheme and hostname (RFC 3986 specifies scheme and host are case-insensitive).
    5. Standardize default ports (remove :80 for http, :443 for https).
    6. Normalize path by resolving redundant segments and standardizing trailing slashes.
    
    Args:
        url: The raw URL string extracted from HTML or user input.
        base_url: The URL of the page where this link was found (for resolving relative paths).
        
    Returns:
        The normalized absolute URL string, or None if the URL is invalid or unsupported.
    """
    if not url:
        return None

    cleaned_url = url.strip()

    # Discard non-HTTP protocols commonly found in hrefs
    ignored_prefixes = ("javascript:", "mailto:", "tel:", "data:", "ftp:", "file:")
    if cleaned_url.lower().startswith(ignored_prefixes):
        return None

    # Step 1: Convert relative URL to absolute URL using base_url if available
    if base_url:
        cleaned_url = urljoin(base_url, cleaned_url)

    # Step 2: Strip fragment identifiers (e.g. #section is stripped)
    cleaned_url, _ = urldefrag(cleaned_url)
    if not cleaned_url:
        return None

    # Step 3: Parse the URL components
    try:
        parsed = urlparse(cleaned_url)
    except Exception:
        return None

    # Step 4: Validate scheme
    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        return None

    # Step 5: Validate and normalize hostname
    hostname = parsed.hostname
    if not hostname:
        return None
    hostname = hostname.lower()

    # Step 6: Handle port normalization
    port = parsed.port
    netloc = hostname
    if port is not None:
        if not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
            netloc = f"{hostname}:{port}"

    # Step 7: Normalize path
    path = parsed.path
    if not path:
        path = "/"
    else:
        # Replace multiple consecutive slashes with a single slash
        path = re.sub(r"/+", "/", path)
        # Standardize trailing slash: root is '/', non-root removes trailing slash for consistency
        if len(path) > 1 and path.endswith("/"):
            path = path.rstrip("/")

    # Reconstruct normalized URL
    # (scheme, netloc, path, params, query, fragment)
    normalized = urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))
    return normalized
