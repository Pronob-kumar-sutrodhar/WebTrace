"""
Unit tests for exporter module: CSV and JSON serialization.
"""

import csv
import json
import os
import tempfile
from webtrace.crawler import CrawledPage
from webtrace.exporter import export_all, export_crawled_pages_csv, export_link_graph_json
from webtrace.graph import LinkGraph


class TestExporter:
    """Test suite for data exporter."""

    def test_export_crawled_pages_csv(self):
        pages = [
            CrawledPage(
                url="https://example.com/",
                title="Home",
                depth=0,
                parent_url=None,
                outgoing_links=["https://example.com/about", "https://example.com/blog"],
            ),
            CrawledPage(
                url="https://example.com/about",
                title="About Us",
                depth=1,
                parent_url="https://example.com/",
                outgoing_links=["https://example.com/"],
            ),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "crawled_pages.csv")
            export_crawled_pages_csv(pages, csv_path)

            assert os.path.exists(csv_path)

            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = list(csv.reader(f))

            assert reader[0] == ["URL", "Title", "Depth", "Parent URL", "Outgoing Links", "Content Snippet", "Extracted Items"]
            assert len(reader) == 3  # Header + 2 rows
            assert reader[1][0] == "https://example.com/"
            assert reader[1][1] == "Home"
            assert reader[1][2] == "0"
            assert reader[1][4] == "2"

    def test_export_link_graph_json(self):
        graph = LinkGraph()
        graph.add_edge("https://example.com/", "https://example.com/about")
        graph.add_edge("https://example.com/about", "https://example.com/")

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "link_graph.json")
            export_link_graph_json(graph, json_path)

            assert os.path.exists(json_path)

            with open(json_path, mode="r", encoding="utf-8") as f:
                data = json.load(f)

            assert data == {
                "https://example.com/": ["https://example.com/about"],
                "https://example.com/about": ["https://example.com/"],
            }

    def test_export_all_convenience(self):
        pages = [
            CrawledPage(
                url="https://example.com/",
                title="Home",
                depth=0,
                parent_url=None,
                outgoing_links=[],
            )
        ]
        graph = LinkGraph()
        graph.add_node("https://example.com/")

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path, json_path = export_all(pages, graph, output_dir=tmpdir)
            assert os.path.exists(csv_path)
            assert os.path.exists(json_path)
