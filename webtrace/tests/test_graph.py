"""
Unit tests for the LinkGraph adjacency list representation in WebTrace.
"""

from webtrace.graph import LinkGraph


class TestLinkGraph:
    """Test suite for LinkGraph data structure."""

    def test_empty_graph(self):
        graph = LinkGraph()
        assert graph.node_count == 0
        assert graph.edge_count == 0
        assert graph.to_dict() == {}

    def test_add_node(self):
        graph = LinkGraph()
        graph.add_node("https://example.com/")
        assert graph.node_count == 1
        assert "https://example.com/" in graph
        assert graph.get_outgoing_edges("https://example.com/") == []

    def test_add_edge_and_adjacency_list(self):
        graph = LinkGraph()
        u = "https://example.com/"
        v1 = "https://example.com/about"
        v2 = "https://example.com/contact"

        graph.add_edge(u, v1)
        graph.add_edge(u, v2)

        assert graph.node_count == 3  # u, v1, v2
        assert graph.edge_count == 2
        assert graph.get_outgoing_edges(u) == [v1, v2]
        assert graph.get_outgoing_edges(v1) == []
        assert graph.get_outgoing_edges(v2) == []

    def test_duplicate_edge_deduplication(self):
        graph = LinkGraph()
        u = "https://example.com/"
        v = "https://example.com/about"

        # Add the same edge twice (parallel edge avoidance)
        graph.add_edge(u, v)
        graph.add_edge(u, v)

        assert graph.edge_count == 1
        assert graph.get_outgoing_edges(u) == [v]

    def test_to_dict_export(self):
        graph = LinkGraph()
        graph.add_edge("https://example.com/", "https://example.com/about")
        graph.add_edge("https://example.com/about", "https://example.com/")

        expected = {
            "https://example.com/": ["https://example.com/about"],
            "https://example.com/about": ["https://example.com/"],
        }
        assert graph.to_dict() == expected
