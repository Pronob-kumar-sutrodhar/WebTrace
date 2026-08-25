"""
================================================================================
WebTrace: Comprehensive HTML Parsing & Content Extraction Module
================================================================================
DSA Concept Demonstrated:
- String Tokenization, DOM Traversal, Document Parsing & Link Extraction.

Extracts all page content types:
1. All Text Elements (headings, paragraphs, quotes, list items, descriptions)
2. Linked Documents & Files (PDF, Word, Excel, ZIP, Text, CSV, JSON)
3. Discovered URLs (internal hyperlinks & external reference links)
4. Page Metadata & Snippet
================================================================================
"""

import re
from typing import Dict, List, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

DOCUMENT_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".tar", ".gz", ".7z", ".txt", ".csv", ".json", ".xml"
}


def extract_comprehensive_page_data(
    html: str, base_url: str = ""
) -> Tuple[str, List[str], str, List[str], List[Dict[str, str]], List[str]]:
    """
    Comprehensively parses an HTML page extracting:
    - Page Title
    - Raw Internal/External Anchor Hrefs (for BFS crawl)
    - Content Snippet
    - All Text Blocks (headings, paragraphs, blockquotes, lists)
    - Linked Documents & Downloads (PDF, DOCX, ZIP, etc.)
    - All Discovered Absolute URLs (both internal and external)

    Returns:
        (title, raw_links, snippet, text_blocks, documents, all_urls)
    """
    if not html:
        return "Untitled", [], "", [], [], []

    soup = BeautifulSoup(html, "html.parser")

    # Remove script, style, noscript, svg, nav, footer to isolate readable content
    for elem in soup(["script", "style", "noscript", "svg"]):
        elem.extract()

    # 1. Page Title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"

    # 2. Extract All Anchor Tags & Classify Links + Documents
    raw_links: List[str] = []
    all_urls: List[str] = []
    documents: List[Dict[str, str]] = []
    seen_urls = set()

    for a in soup.find_all("a", href=True):
        raw_href = a["href"].strip()
        if not raw_href or raw_href.startswith(("javascript:", "mailto:", "tel:", "#")):
            continue

        raw_links.append(raw_href)

        # Resolve absolute URL
        abs_url = urljoin(base_url, raw_href) if base_url else raw_href
        if abs_url not in seen_urls:
            seen_urls.add(abs_url)
            all_urls.append(abs_url)

            # Check if link points to a document or downloadable file
            path = urlparse(abs_url).path.lower()
            for ext in DOCUMENT_EXTENSIONS:
                if path.endswith(ext):
                    link_text = a.get_text(" ", strip=True) or path.split("/")[-1]
                    documents.append({
                        "url": abs_url,
                        "filename": path.split("/")[-1] or abs_url,
                        "type": ext.replace(".", "").upper(),
                        "text": link_text,
                    })
                    break

    # 3. Extract All Text Blocks (Headings, Paragraphs, Quotes, Lists, Articles)
    text_blocks: List[str] = []

    # Priority 1: Structured Quote Blocks (e.g. quotes.toscrape.com)
    quote_elements = soup.find_all(class_=re.compile(r"\bquote\b", re.I)) or soup.find_all("blockquote")
    if quote_elements:
        for q in quote_elements[:30]:
            text_el = q.find(class_=re.compile(r"\btext\b", re.I)) or q
            author_el = q.find(class_=re.compile(r"\bauthor\b", re.I))
            tags_el = q.find(class_=re.compile(r"\btags?\b", re.I))

            quote_text = text_el.get_text(" ", strip=True)
            author_text = author_el.get_text(" ", strip=True) if author_el else ""
            tag_texts = [t.get_text(strip=True) for t in q.find_all(class_=re.compile(r"\btag\b", re.I))] if tags_el else []

            if quote_text:
                formatted = quote_text
                if author_text:
                    formatted += f" — {author_text}"
                if tag_texts:
                    clean_tags = [t for t in tag_texts if t.lower() != "tags:"]
                    if clean_tags:
                        formatted += f" [Tags: {', '.join(clean_tags[:5])}]"
                if formatted not in text_blocks:
                    text_blocks.append(formatted)

    # Priority 2: Author Bios, Article Bodies, Post Content
    content_containers = soup.find_all(class_=re.compile(r"(author-description|description|article-body|post-content|entry-content|summary|content-body)", re.I))
    if content_containers:
        for container in content_containers[:15]:
            text = container.get_text(" ", strip=True)
            if text and len(text) > 10 and text not in text_blocks:
                text_blocks.append(text)

    # Priority 3: All Headings & Paragraphs & Lists across the document
    general_elements = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "dt", "dd", "td"])
    for elem in general_elements:
        t = elem.get_text(" ", strip=True)
        if t and len(t) > 3 and t not in text_blocks:
            text_blocks.append(t)

    # If still empty, grab raw body text
    if not text_blocks:
        body_text = soup.get_text(" ", strip=True)
        if body_text:
            text_blocks.append(body_text[:500])

    # 4. Content Snippet (Meta description or first text block)
    meta_desc = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
    if meta_desc and meta_desc.get("content"):
        snippet = meta_desc["content"].strip()
    elif text_blocks:
        snippet = text_blocks[0]
    else:
        snippet = title

    if len(snippet) > 250:
        snippet = snippet[:247] + "..."

    return title, raw_links, snippet, text_blocks, documents, all_urls


def extract_page_data(html: str) -> Tuple[str, List[str], str, List[str]]:
    """Backward-compatible wrapper returning (title, raw_links, snippet, text_blocks)."""
    title, raw_links, snippet, text_blocks, _, _ = extract_comprehensive_page_data(html)
    return title, raw_links, snippet, text_blocks


def extract_links_and_title(html: str) -> Tuple[str, List[str]]:
    """Legacy helper returning only title and links."""
    title, links, _, _ = extract_page_data(html)
    return title, links
