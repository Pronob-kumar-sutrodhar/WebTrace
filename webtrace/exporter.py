"""
================================================================================
WebTrace: Data Exporter Module (CSV & JSON Adjacency List Serialization)
================================================================================
DSA Concept Demonstrated:
- Data Structure Serialization:
  1. Tabular Representation of BFS Traversal Metadata (CSV).
  2. Adjacency List Graph Representation Serialization (JSON).

Why this matters for Algorithm Output:
- The BFS traversal yields both a linear sequence of visited nodes (with search
  tree metadata: depth, parent pointer) and a non-linear Directed Graph of links.
- The CSV file captures the BFS exploration trace and tree properties (node u,
  depth d, parent p, out-degree deg+(u)).
- The JSON file serializes the full Adjacency List graph structure G = (V, E),
  enabling downstream graph visualization, network analysis, and PageRank calculations.
================================================================================
"""

import csv
import json
import os
from typing import List, Tuple
from webtrace.crawler import CrawledPage
from webtrace.graph import LinkGraph


def export_crawled_pages_csv(pages: List[CrawledPage], filepath: str) -> str:
    """
    Exports the list of crawled pages to a CSV file.

    Columns:
    - URL: The canonical URL of the crawled page.
    - Title: Extracted <title> text.
    - Depth: Distance (in clicks/hops) from the seed page in the BFS tree.
    - Parent URL: The URL of the page that first linked to this page.
    - Outgoing Links: Total number of valid internal outgoing links (out-degree).

    Args:
        pages: List of CrawledPage dataclass instances.
        filepath: Destination path for the CSV file.

    Returns:
        The absolute path to the written CSV file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    headers = ["URL", "Title", "Depth", "Parent URL", "Outgoing Links", "Content Snippet", "Extracted Items"]

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for page in pages:
            extracted_str = " | ".join(page.extracted_data[:5]) if page.extracted_data else ""
            writer.writerow([
                page.url,
                page.title,
                page.depth,
                page.parent_url if page.parent_url else "—",
                page.outgoing_count,
                page.snippet,
                extracted_str,
            ])

    return os.path.abspath(filepath)


def export_link_graph_json(graph: LinkGraph, filepath: str, indent: int = 2) -> str:
    """
    Exports the LinkGraph adjacency list to a JSON file.

    Format:
    {
      "https://example.com/": [
        "https://example.com/about",
        "https://example.com/contact"
      ],
      "https://example.com/about": [
        "https://example.com/"
      ]
    }

    Args:
        graph: LinkGraph instance containing the directed graph.
        filepath: Destination path for the JSON file.
        indent: Indentation spaces for pretty-printed JSON.

    Returns:
        The absolute path to the written JSON file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    with open(filepath, mode="w", encoding="utf-8") as f:
        json.dump(graph.to_dict(), f, indent=indent, ensure_ascii=False)

    return os.path.abspath(filepath)


def export_all(
    pages: List[CrawledPage],
    graph: LinkGraph,
    output_dir: str = "output",
) -> Tuple[str, str]:
    """
    Convenience function to export both CSV and JSON artifacts into the target directory.

    Args:
        pages: Crawled page records.
        graph: Discovered LinkGraph.
        output_dir: Directory where output files will be created.

    Returns:
        Tuple of (csv_filepath, json_filepath).
    """
    csv_path = os.path.join(output_dir, "crawled_pages.csv")
    json_path = os.path.join(output_dir, "link_graph.json")

    exported_csv = export_crawled_pages_csv(pages, csv_path)
    exported_json = export_link_graph_json(graph, json_path)

    return exported_csv, exported_json
