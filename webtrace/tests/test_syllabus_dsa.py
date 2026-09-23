"""
================================================================================
WebTrace: Automated Tests for Syllabus-Aligned Data Structures & Algorithms
================================================================================
Course: ECE 2103 - Data Structure & Algorithms
Tests verify:
1. Vector (Linear Array): Memory representation, dynamic resizing, linear search O(N), binary search O(log N).
2. MinHeapPriorityQueue: Min-heap invariant, push/pop O(log N).
3. BinarySearchTree: Insertion, search, 3-case deletion, in-order traversal sorting.
4. LinkGraph & Dijkstra: Shortest weighted path computation.
5. WebCrawler integration with Vector and BST.
6. Flask endpoints for Dijkstra and BST in-order queries.
================================================================================
"""

import json
from typing import Dict, List, Optional
import pytest

from webtrace.app import app
from webtrace.crawler import CrawledPage, WebCrawler
from webtrace.graph import LinkGraph
from webtrace.structures import BinarySearchTree, MinHeapPriorityQueue, Vector


# ==============================================================================
# 1. VECTOR (LINEAR ARRAY) TESTS
# ==============================================================================
class TestVector:
    """Test suite for Linear Dynamic Array matching ECE 2103 syllabus."""

    def test_initialization_and_capacity(self):
        vec: Vector[str] = Vector[str](initial_capacity=4)
        assert vec.size == 0
        assert vec.capacity == 4
        assert vec.is_empty() is True

    def test_push_back_and_dynamic_resizing(self):
        vec: Vector[int] = Vector[int](initial_capacity=2)
        vec.push_back(10)
        vec.push_back(20)
        assert vec.size == 2
        assert vec.capacity == 2

        # Exceed capacity: triggers doubling resize to 4
        vec.push_back(30)
        assert vec.size == 3
        assert vec.capacity == 4
        assert vec.get(0) == 10
        assert vec.get(1) == 20
        assert vec.get(2) == 30

    def test_linear_search_and_contains(self):
        vec: Vector[str] = Vector[str]()
        vec.push_back("https://example.com/")
        vec.push_back("https://example.com/about")
        vec.push_back("https://example.com/contact")

        # Linear Search: Best Case index 0
        assert vec.linear_search("https://example.com/") == 0
        # Linear Search: Intermediate
        assert vec.linear_search("https://example.com/about") == 1
        # Linear Search: Absent
        assert vec.linear_search("https://example.com/missing") == -1

        # Membership test
        assert "https://example.com/about" in vec
        assert ("https://other.com/" in vec) is False
        assert vec.contains("https://example.com/contact") is True

    def test_binary_search(self):
        vec: Vector[int] = Vector[int]()
        # Insert sorted elements
        for val in [5, 12, 23, 34, 45, 56, 67, 78, 89, 99]:
            vec.push_back(val)

        assert vec.binary_search(5) == 0
        assert vec.binary_search(56) == 5
        assert vec.binary_search(99) == 9
        assert vec.binary_search(100) == -1
        assert vec.binary_search(1) == -1


# ==============================================================================
# 2. PRIORITY QUEUE / BINARY MIN-HEAP TESTS
# ==============================================================================
class TestMinHeapPriorityQueue:
    """Test suite for Min-Heap Priority Queue matching ECE 2103 syllabus."""

    def test_heap_push_pop_order(self):
        pq: MinHeapPriorityQueue[str] = MinHeapPriorityQueue[str]()
        pq.push(15.5, "Task C")
        pq.push(3.2, "Task A")
        pq.push(8.7, "Task B")
        pq.push(1.0, "Root Priority")

        assert len(pq) == 4
        p, item = pq.pop()
        assert p == 1.0
        assert item == "Root Priority"

        p, item = pq.pop()
        assert p == 3.2
        assert item == "Task A"

        p, item = pq.pop()
        assert p == 8.7
        assert item == "Task B"

        p, item = pq.pop()
        assert p == 15.5
        assert item == "Task C"

        assert pq.is_empty() is True

    def test_empty_heap_exception(self):
        pq: MinHeapPriorityQueue[int] = MinHeapPriorityQueue[int]()
        with pytest.raises(IndexError):
            pq.pop()
        with pytest.raises(IndexError):
            pq.peek()


# ==============================================================================
# 3. BINARY SEARCH TREE (BST) TESTS
# ==============================================================================
class TestBinarySearchTree:
    """Test suite for Binary Search Tree matching ECE 2103 syllabus."""

    def test_bst_insert_and_search(self):
        bst: BinarySearchTree[str] = BinarySearchTree[str]()
        bst.insert("cherry", "fruit #3")
        bst.insert("apple", "fruit #1")
        bst.insert("banana", "fruit #2")
        bst.insert("date", "fruit #4")

        assert bst.count == 4
        assert bst.search("apple") == "fruit #1"
        assert bst.search("banana") == "fruit #2"
        assert bst.search("cherry") == "fruit #3"
        assert bst.search("fig") is None
        assert "date" in bst

    def test_bst_inorder_traversal_strictly_sorted(self):
        bst: BinarySearchTree[int] = BinarySearchTree[int]()
        # Unsorted sequence of URLs
        urls = [
            "https://example.com/z",
            "https://example.com/a",
            "https://example.com/m",
            "https://example.com/b",
            "https://example.com/c",
        ]
        for idx, u in enumerate(urls):
            bst.insert(u, idx)

        inorder = bst.inorder_traversal()
        keys = [k for k, _ in inorder]
        # In-order traversal must be strictly ascending
        assert keys == sorted(urls)

    def test_bst_deletion_three_cases(self):
        bst: BinarySearchTree[str] = BinarySearchTree[str]()
        # Construct tree:
        #          50
        #        /    \
        #       30    70
        #      /  \   /  \
        #     20  40 60  80
        for val in ["50", "30", "70", "20", "40", "60", "80"]:
            bst.insert(val, f"val_{val}")

        assert bst.count == 7

        # Case 1: Delete a leaf node ("20")
        assert bst.delete("20") is True
        assert bst.search("20") is None
        assert bst.count == 6

        # Case 2: Delete node with 1 child
        # Make "30" have only 1 child ("40")
        assert bst.delete("30") is True
        assert bst.search("30") is None
        assert bst.search("40") == "val_40"
        assert bst.count == 5

        # Case 3: Delete node with 2 children ("50" root, successor is "60")
        assert bst.delete("50") is True
        assert bst.search("50") is None
        assert bst.count == 4

        # Remaining nodes must still maintain in-order sorted property
        inorder_keys = [k for k, _ in bst.inorder_traversal()]
        assert inorder_keys == ["40", "60", "70", "80"]


# ==============================================================================
# 4. GRAPH & DIJKSTRA'S SHORTEST PATH TESTS
# ==============================================================================
class TestDijkstraShortestPath:
    """Test suite for Dijkstra's Algorithm on LinkGraph matching ECE 2103."""

    def test_dijkstra_weighted_shortest_path(self):
        """
        Graph topology:
        Seed: /home
          |-- (weight 10) --> /fast_route -- (weight 5) --> /destination  (Total: 15)
          |-- (weight 2)  --> /slow_route -- (weight 30) -> /destination  (Total: 32)
        
        Unweighted BFS would choose: /home -> /slow_route -> /destination (both are 2 hops)
        Weighted Dijkstra MUST choose: /home -> /fast_route -> /destination (cost 15 < 32)
        """
        graph = LinkGraph()
        graph.add_edge("/home", "/fast_route", weight=10.0)
        graph.add_edge("/fast_route", "/destination", weight=5.0)

        graph.add_edge("/home", "/slow_route", weight=2.0)
        graph.add_edge("/slow_route", "/destination", weight=30.0)

        cost, path = graph.dijkstra_shortest_path("/home", "/destination")
        assert cost == 15.0
        assert path == ["/home", "/fast_route", "/destination"]

    def test_dijkstra_cyclic_graph(self):
        graph = LinkGraph()
        graph.add_edge("A", "B", weight=2.0)
        graph.add_edge("B", "A", weight=2.0)  # Cycle
        graph.add_edge("B", "C", weight=4.0)
        graph.add_edge("C", "D", weight=1.0)

        cost, path = graph.dijkstra_shortest_path("A", "D")
        assert cost == 7.0
        assert path == ["A", "B", "C", "D"]

    def test_dijkstra_unreachable_node(self):
        graph = LinkGraph()
        graph.add_edge("A", "B", weight=3.0)
        graph.add_node("Isolated")

        cost, path = graph.dijkstra_shortest_path("A", "Isolated")
        assert cost == float("inf")
        assert path == []


# ==============================================================================
# 5. WEBCRAWLER WITH VECTOR & BST INTEGRATION TESTS
# ==============================================================================
class MockFetcher:
    def __init__(self, pages: Dict[str, str]) -> None:
        self.pages = pages

    def fetch(self, url: str) -> Optional[str]:
        return self.pages.get(url, None)


class TestCrawlerSyllabusIntegration:
    """Verifies WebCrawler uses Vector and BST matching syllabus."""

    def test_crawler_uses_vector_and_bst(self):
        mock_site = {
            "https://test.com/": '<html><head><title>Home</title></head><body><a href="/page1">P1</a></body></html>',
            "https://test.com/page1": '<html><head><title>Page 1</title></head><body><a href="/">Back</a></body></html>',
        }
        fetcher = MockFetcher(mock_site)
        crawler = WebCrawler(
            seed_url="https://test.com/",
            max_depth=2,
            max_pages=5,
            fetcher=fetcher,
            verbose=False,
        )

        # Confirm structures are the new syllabus types
        assert isinstance(crawler.visited, Vector)
        assert isinstance(crawler.bst_index, BinarySearchTree)

        pages, graph = crawler.crawl()

        # Visited Vector must contain crawled URLs
        assert len(crawler.visited) == 2
        assert "https://test.com/" in crawler.visited
        assert "https://test.com/page1" in crawler.visited

        # BST Index must contain records searchable by URL
        rec_home = crawler.bst_index.search("https://test.com/")
        assert rec_home is not None
        assert rec_home.title == "Home"

        rec_p1 = crawler.bst_index.search("https://test.com/page1")
        assert rec_p1 is not None
        assert rec_p1.title == "Page 1"

        # BST In-order traversal must return items sorted alphabetically
        inorder = crawler.bst_index.inorder_traversal()
        assert len(inorder) == 2
        assert inorder[0][0] == "https://test.com/"
        assert inorder[1][0] == "https://test.com/page1"


# ==============================================================================
# 6. FLASK API ENDPOINT TESTS (DIJKSTRA & BST IN-ORDER)
# ==============================================================================
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestFlaskSyllabusEndpoints:
    def test_dijkstra_endpoint_after_crawl(self, client):
        # Perform dry-run crawl first to populate graph
        client.post(
            "/api/crawl",
            data=json.dumps({"seed": "https://example.com/", "dry_run": True}),
            content_type="application/json",
        )

        # Query Dijkstra endpoint
        payload = {
            "start_url": "https://example.com/",
            "target_url": "https://example.com/",
        }
        res = client.post(
            "/api/graph/shortest-path",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["cost"] == 0.0
        assert data["path"] == ["https://example.com/"]

    def test_bst_inorder_endpoint(self, client):
        # Trigger crawl
        client.post(
            "/api/crawl",
            data=json.dumps({"seed": "https://example.com/", "max_depth": 0, "max_pages": 1}),
            content_type="application/json",
        )

        res = client.get("/api/pages/bst-inorder")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "traversal" in data
        assert data["traversal"] == "In-Order (Left -> Root -> Right)"
        assert len(data["pages"]) >= 0
