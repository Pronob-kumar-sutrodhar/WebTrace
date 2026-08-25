"""
Unit tests for HTML parser and link extraction in WebTrace.
"""

from webtrace.parser import extract_links_and_title


class TestParser:
    """Test suite for extract_links_and_title."""

    def test_extract_valid_html(self):
        html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Test Page Title</title>
            </head>
            <body>
                <p>Welcome</p>
                <a href="/about">About Us</a>
                <a href="https://example.com/contact">Contact</a>
                <a href="/docs#section">Docs</a>
            </body>
        </html>
        """
        title, links = extract_links_and_title(html)
        assert title == "Test Page Title"
        assert links == ["/about", "https://example.com/contact", "/docs#section"]

    def test_empty_or_malformed_html(self):
        title, links = extract_links_and_title("")
        assert title == "Untitled"
        assert links == []

        title, links = extract_links_and_title("<div>No title or links here</div>")
        assert title == "Untitled"
        assert links == []

    def test_anchor_without_href(self):
        html = '<html><head><title>Page</title></head><body><a>No href</a><a href="/valid">Valid</a></body></html>'
        title, links = extract_links_and_title(html)
        assert title == "Page"
        assert links == ["/valid"]
