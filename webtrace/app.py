"""
================================================================================
WebTrace: Interactive Web Dashboard (Flask Application)
================================================================================
Provides a graphical user interface where users can input a URL, configure crawl
parameters, view real-time crawl statistics, inspect the tabular BFS traversal
search tree, and interact with a visual Node-Link Graph of the website.

Usage:
    python -m webtrace.app
    or
    python webtrace/app.py
================================================================================
"""

import os
import sys
import time
import webbrowser
from dataclasses import asdict
from typing import Any, Dict

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify, render_template, request, send_file
from webtrace.crawler import WebCrawler
from webtrace.exporter import export_all
from webtrace.fetcher import Fetcher
from webtrace.graph import LinkGraph
from webtrace.url_utils import normalize_url

FRONTEND_DIST = os.path.join(PROJECT_ROOT, "frontend", "dist")
OUTPUT_DIR = os.path.join(CURRENT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

if os.path.exists(FRONTEND_DIST):
    app = Flask(
        __name__,
        static_folder=os.path.join(FRONTEND_DIST, "assets"),
        static_url_path="/assets",
        template_folder=FRONTEND_DIST,
    )
else:
    app = Flask(
        __name__,
        template_folder=os.path.join(CURRENT_DIR, "templates"),
    )


@app.after_request
def add_cors_headers(response):
    """Enable CORS so Vite dev server (localhost:5173) can talk to API."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    """Renders the React frontend application or fallback HTML."""
    if os.path.exists(os.path.join(FRONTEND_DIST, "index.html")):
        return send_file(os.path.join(FRONTEND_DIST, "index.html"))
    return render_template("index.html")


@app.route("/api/crawl", methods=["POST"])
def api_crawl():
    """
    API endpoint that accepts crawl parameters, executes the BFS crawler,
    and returns the collected pages, graph adjacency list, and crawl statistics.
    """
    data: Dict[str, Any] = request.get_json() or {}

    raw_seed = data.get("seed", "").strip()
    max_depth = int(data.get("max_depth", 2))
    max_pages = int(data.get("max_pages", 10))
    delay = float(data.get("delay", 0.5))
    respect_robots = bool(data.get("respect_robots", True))
    dry_run = bool(data.get("dry_run", False))

    canonical_seed = normalize_url(raw_seed)
    if not canonical_seed:
        return jsonify({
            "status": "error",
            "message": f"Invalid seed URL: '{raw_seed}'. Please provide a valid HTTP/HTTPS address.",
        }), 400

    start_time = time.time()

    if dry_run:
        # Simulate crawl setup without network requests
        graph = LinkGraph()
        graph.add_node(canonical_seed)
        elapsed = time.time() - start_time
        return jsonify({
            "status": "success",
            "pages": [],
            "graph": graph.to_dict(),
            "stats": {
                "total_crawled": 0,
                "graph_nodes": 1,
                "graph_edges": 0,
                "duration_seconds": elapsed,
                "dry_run": True,
            },
        })

    # Real crawl execution
    fetcher = Fetcher(
        delay=delay,
        timeout=5.0,
        respect_robots=respect_robots,
    )

    crawler = WebCrawler(
        seed_url=canonical_seed,
        max_depth=max_depth,
        max_pages=max_pages,
        fetcher=fetcher,
        verbose=False,
    )

    crawled_pages, graph = crawler.crawl()
    elapsed = time.time() - start_time

    # Export to disk for downloading
    export_all(crawled_pages, graph, output_dir=OUTPUT_DIR)

    # Format page records for JSON response
    pages_json = [
        {
            "url": p.url,
            "title": p.title,
            "depth": p.depth,
            "parent_url": p.parent_url,
            "outgoing_count": p.outgoing_count,
            "outgoing_links": p.outgoing_links,
            "snippet": p.snippet,
            "text_blocks": p.text_blocks,
            "documents": p.documents,
            "all_urls": p.all_urls,
            "extracted_data": p.text_blocks,  # backward compatibility
        }
        for p in crawled_pages
    ]

    total_text_blocks = sum(len(p.text_blocks) for p in crawled_pages)
    total_docs = sum(len(p.documents) for p in crawled_pages)
    total_urls = sum(len(p.all_urls) for p in crawled_pages)

    # Generate helpful feedback message
    if len(crawled_pages) == 0:
        info_message = "No pages were crawled. The target server may be blocking requests, returned a 403/404, or is disallowed by robots.txt. Try unchecking 'Respect robots.txt' or test with 'https://quotes.toscrape.com/'."
    elif len(crawled_pages) == 1 and crawled_pages[0].outgoing_count == 0:
        info_message = f"Crawled 1 page ('{crawled_pages[0].title}'). Extracted {total_text_blocks} text blocks, {total_docs} documents, and {total_urls} URLs."
    else:
        info_message = f"Successfully crawled {len(crawled_pages)} pages. Extracted {total_text_blocks} text blocks, {total_docs} documents, and {total_urls} total URLs across {graph.node_count} graph nodes."

    return jsonify({
        "status": "success",
        "message": info_message,
        "pages": pages_json,
        "graph": graph.to_dict(),
        "stats": {
            "total_crawled": len(crawled_pages),
            "total_text_blocks": total_text_blocks,
            "total_documents": total_docs,
            "total_discovered_urls": total_urls,
            "graph_nodes": graph.node_count,
            "graph_edges": graph.edge_count,
            "duration_seconds": elapsed,
            "dry_run": False,
        },
    })


@app.route("/api/download/csv")
def download_csv():
    """Serves the generated crawled_pages.csv file."""
    csv_file = os.path.join(OUTPUT_DIR, "crawled_pages.csv")
    if os.path.exists(csv_file):
        return send_file(csv_file, as_attachment=True, download_name="crawled_pages.csv")
    return jsonify({"error": "No CSV data available yet. Please run a crawl first."}), 404


@app.route("/api/download/json")
def download_json():
    """Serves the generated link_graph.json file."""
    json_file = os.path.join(OUTPUT_DIR, "link_graph.json")
    if os.path.exists(json_file):
        return send_file(json_file, as_attachment=True, download_name="link_graph.json")
    return jsonify({"error": "No JSON data available yet. Please run a crawl first."}), 404


def run_app(host: str = "127.0.0.1", port: int = 5000, open_browser: bool = True):
    """Starts the Flask web application."""
    url = f"http://{host}:{port}"
    print("=" * 75)
    print("  WebTrace: React & Tailwind Web Dashboard")
    print(f"  Running at: {url}")
    print("  Press CTRL+C to stop the server.")
    print("=" * 75)

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="WebTrace Web Dashboard Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=5000, help="Port number")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open the browser")
    args = parser.parse_args()

    run_app(host=args.host, port=args.port, open_browser=not args.no_browser)
