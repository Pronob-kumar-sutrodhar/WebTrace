"""
================================================================================
WebTrace: Graph Representation Module (Adjacency List)
================================================================================
DSA Concept Demonstrated:
- Graph Data Structure: Directed Graph represented as an Adjacency List.

Why this matters for Data Structures & Algorithm Design:
A website can be modeled mathematically as a Directed Graph G = (V, E):
  - Vertices (V): Web pages (identified by their canonical URLs).
  - Directed Edges (E): Hyperlinks from a source page (u) pointing to a target (v).

Why Adjacency List over Adjacency Matrix?
1. Space Complexity:
   - Adjacency Matrix requires O(V^2) memory. For large websites with thousands
     of pages, allocating a V x V matrix would consume prohibitive amounts of memory.
   - Adjacency List requires O(V + E) memory, storing only existing hyperlinks.
     Since the Web is a sparse graph (average outgoing degree d << V), the
     adjacency list is optimally memory-efficient.
2. Traversal Efficiency:
   - In BFS traversal, iterating over outgoing neighbors of a node u takes O(deg(u))
     time in an Adjacency List, compared to O(V) time scanning an entire row in
     an Adjacency Matrix.
================================================================================
"""

from typing import Dict, List, Optional, Set, Tuple

from webtrace.structures import MinHeapPriorityQueue


class LinkGraph:
    """
    Represents the internal hyperlink structure of a website as a Directed Graph
    using an Adjacency List (dictionary mapping each source URL to a list of target URLs).
    """

    def __init__(self) -> None:
        """
        Initializes an empty graph.
        
        Internal Representation:
            _adj: dict[str, list[str]] where keys are vertex URLs and values
                  are lists of directed outgoing neighbor URLs.
            _edge_set: dict[str, set[str]] helper to enforce O(1) deduplication
                       of parallel edges between the same pair of nodes (u -> v).
            _weights: dict[tuple[str, str], float] storing edge weights (e.g. latency/cost).
        """
        self._adj: Dict[str, List[str]] = {}
        self._edge_set: Dict[str, Set[str]] = {}
        self._weights: Dict[Tuple[str, str], float] = {}

    def add_node(self, node: str) -> None:
        """
        Adds a vertex (URL) to the graph if it is not already present.
        
        Time Complexity: O(1) average-time dictionary lookup and insertion.
        
        Args:
            node: The canonical URL of the web page.
        """
        if node not in self._adj:
            self._adj[node] = []
            self._edge_set[node] = set()

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> None:
        """
        Adds a directed edge (hyperlink) from `source` page to `target` page: (u -> v).
        
        Ensures both vertices exist in the graph. Avoids creating duplicate parallel
        edges if the same link appears multiple times on the source page.
        
        Time Complexity: O(1) average-time insertion and set membership check.
        
        Args:
            source: The originating page URL (u).
            target: The destination page URL (v).
            weight: The cost / latency of following this edge (default 1.0).
        """
        self.add_node(source)
        self.add_node(target)

        # Store or update the weight for this edge
        self._weights[(source, target)] = weight

        # Avoid duplicate parallel edges (u -> v)
        if target not in self._edge_set[source]:
            self._edge_set[source].add(target)
            self._adj[source].append(target)

    def get_outgoing_edges(self, node: str) -> List[str]:
        """
        Retrieves all outgoing neighbor vertices for a given vertex.
        
        Time Complexity: O(1) lookup.
        
        Args:
            node: The URL vertex whose outgoing links are requested.
            
        Returns:
            A copy of the list of target URLs linked from this page.
        """
        return list(self._adj.get(node, []))

    def get_edge_weight(self, source: str, target: str) -> float:
        """Returns the weight of directed edge (source -> target). Defaults to 1.0."""
        return self._weights.get((source, target), 1.0)

    def dijkstra_shortest_path(self, start: str, target: str) -> Tuple[float, List[str]]:
        """
        Computes the shortest weighted path from `start` to `target` node using Dijkstra's Algorithm.

        DSA Concepts Demonstrated:
        - Greedy Algorithm
        - Min-Heap Priority Queue (MinHeapPriorityQueue)
        - Predecessor map for path reconstruction
        - Time Complexity: O((V + E) log V)
        - Space Complexity: O(V)

        Args:
            start: Source URL.
            target: Destination URL.

        Returns:
            Tuple of (total_distance, path_as_list_of_urls).
            If unreachable or nodes absent, returns (float('inf'), []).
        """
        if start not in self._adj or target not in self._adj:
            return float("inf"), []

        if start == target:
            return 0.0, [start]

        distances: Dict[str, float] = {node: float("inf") for node in self._adj}
        previous: Dict[str, Optional[str]] = {node: None for node in self._adj}
        distances[start] = 0.0

        pq: MinHeapPriorityQueue[str] = MinHeapPriorityQueue[str]()
        pq.push(0.0, start)

        visited_nodes: Set[str] = set()

        while not pq.is_empty():
            curr_dist, u = pq.pop()

            if u in visited_nodes:
                continue
            visited_nodes.add(u)

            if u == target:
                break

            for v in self.get_outgoing_edges(u):
                weight = self.get_edge_weight(u, v)
                alt = curr_dist + weight

                if alt < distances[v]:
                    distances[v] = alt
                    previous[v] = u
                    pq.push(alt, v)

        if distances[target] == float("inf"):
            return float("inf"), []

        # Reconstruct path from target back to start
        path: List[str] = []
        curr: Optional[str] = target
        while curr is not None:
            path.append(curr)
            curr = previous.get(curr)
        path.reverse()

        return distances[target], path

    def get_nodes(self) -> List[str]:
        """
        Returns a list of all vertices (URLs) currently in the graph.
        
        Returns:
            List of all discovered node URLs.
        """
        return list(self._adj.keys())

    @property
    def node_count(self) -> int:
        """Returns the total number of vertices |V| in the graph."""
        return len(self._adj)

    @property
    def edge_count(self) -> int:
        """Returns the total number of directed edges |E| in the graph."""
        return sum(len(neighbors) for neighbors in self._adj.values())

    def to_dict(self) -> Dict[str, List[str]]:
        """
        Exports the graph structure as a standard Python dictionary of adjacency lists.
        
        This dictionary format maps directly to JSON for serialization:
        {
            "http://example.com/": ["http://example.com/about", "http://example.com/blog"],
            "http://example.com/about": ["http://example.com/"],
            ...
        }
        
        Returns:
            A dictionary representing the full adjacency list.
        """
        return {node: list(neighbors) for node, neighbors in self._adj.items()}

    def __contains__(self, node: str) -> bool:
        """Checks if a vertex exists in the graph: O(1) time complexity."""
        return node in self._adj

    def __len__(self) -> int:
        """Returns the total number of vertices |V|."""
        return len(self._adj)

    def __repr__(self) -> str:
        return f"<LinkGraph: |V|={self.node_count}, |E|={self.edge_count}>"
