# WebTrace: Domain-Restricted BFS Web Crawler

> **Course:** ECE 2103 — Data Structures & Algorithms  
> **Category:** DSA Course Project  
> **Language:** Python 3 + React (Vite + Tailwind CSS)

---

## 1. Project Overview

**WebTrace** is a full-stack, domain-restricted web crawler designed as an educational teaching artifact for Data Structures and Algorithms (DSA). Starting from a single seed URL, WebTrace systematically crawls web pages within the same domain using **Breadth-First Search (BFS)** traversal, builds a directed **Link Graph** representing the website's structure, computes **shortest hyperlink paths** via **Dijkstra's Algorithm**, indexes crawled pages in a **Binary Search Tree (BST)**, and presents everything through an interactive **React + Tailwind CSS** web dashboard.

Results are also exportable to **CSV** and **JSON**.

---

## 2. DSA Concept Mapping

Every module in WebTrace is designed to explicitly demonstrate core Data Structures and Algorithms topics taught in the ECE 2103 syllabus:

| Module | Responsibility | Key Data Structure / Algorithm | Syllabus Topic |
|---|---|---|---|
| [`webtrace/crawler.py`](webtrace/crawler.py) | Orchestrates the BFS traversal loop; controls crawl frontier and visit tracking. | **FIFO Queue** (`collections.deque`), **Visited Set** (`set`), **BST Index** | **Queue (FIFO)**, **Hash Set**, **Breadth-First Search (BFS)** |
| [`webtrace/graph.py`](webtrace/graph.py) | Models the website's hyperlink topology and computes shortest paths. | **Adjacency List** (`dict[str, list[str]]`), **Dijkstra's Algorithm** | **Graph Representation**, **Shortest Path Algorithms** |
| [`webtrace/structures.py`](webtrace/structures.py) | Textbook implementations of custom data structures. | **Vector** (Dynamic Array), **MinHeapPriorityQueue** (Binary Min-Heap), **BinarySearchTree** | **Linear Arrays**, **Heaps**, **Binary Trees & BST** |
| [`webtrace/url_utils.py`](webtrace/url_utils.py) | URL canonicalization, fragment stripping, and domain restriction. | **String Parsing**, **Canonical Hashing Invariant** | **Hashing & Collision Invariants** |
| [`webtrace/fetcher.py`](webtrace/fetcher.py) | Network I/O, `robots.txt` compliance, and politeness rate-limiting. | **Hash Map Caching** (`dict[str, RobotFileParser]`, `dict[str, float]`) | **Hash Tables (Caching & State Tracking)** |
| [`webtrace/parser.py`](webtrace/parser.py) | Extracts `<title>`, `<a href>` links, text blocks, and documents from HTML. | **String Parsing / DOM Tokenization** | **String & Tree Parsing** |
| [`webtrace/exporter.py`](webtrace/exporter.py) | Serializes traversal search tree and adjacency list to disk. | **Tabular Serialization** (CSV) & **Graph Serialization** (JSON) | **Data Structure Serialization** |
| [`webtrace/app.py`](webtrace/app.py) | Flask REST API server; serves the React frontend build. | **REST API**, **CORS** | **System Orchestration** |
| [`webtrace/main.py`](webtrace/main.py) | CLI driver and argument parser. | **Application Driver** | **System Orchestration** |
| [`webtrace/interactive.py`](webtrace/interactive.py) | Interactive terminal-based crawl interface. | **I/O Loop** | **System Orchestration** |

---

## 3. Key Algorithmic Invariants

### A. Breadth-First Search (BFS) & FIFO Queue
- Exploration order is driven by `collections.deque`.
- Vertices are enqueued at the back (`append`) and dequeued from the front (`popleft`).
- **Invariant:** All web pages at distance $d$ (click-distance from seed) are visited before any page at distance $d + 1$, ensuring the discovery of the shortest click path from the seed.

### B. Visited Set & Cycle Prevention
- `self.visited` is implemented using Python's built-in `set` (Hash Table).
- Every newly discovered hyperlink is checked against the set in $\mathcal{O}(1)$ average time.
- **Invariant:** Pages are added to the Visited Set *immediately upon discovery*, preventing duplicate queue insertions and eliminating infinite loops caused by cyclic hyperlinks ($A \to B \to A$).

### C. Adjacency List Graph ($\mathcal{O}(|V| + |E|)$ Space)
- Websites are sparse graphs where $|E| \ll |V|^2$.
- `LinkGraph` uses an Adjacency List (`dict[str, list[str]]`), requiring only $\mathcal{O}(|V| + |E|)$ space, compared to $\mathcal{O}(|V|^2)$ for an Adjacency Matrix.

### D. Dijkstra's Algorithm (Min-Heap Priority Queue)
- `LinkGraph.dijkstra_shortest_path(start_url, target_url)` finds the minimum-hop path between any two crawled pages.
- Uses the custom `MinHeapPriorityQueue` (Binary Min-Heap) from `structures.py`.
- **Invariant:** The Min-Heap always extracts the URL with the smallest accumulated cost (hop count), guaranteeing the first time a node is popped from the heap, it holds its shortest path distance.

### E. Binary Search Tree (BST) — Page Index
- After each page is crawled, it is inserted into a `BinarySearchTree` keyed by URL.
- In-Order traversal (Left → Root → Right) yields all crawled pages in lexicographically sorted order.
- **BST Invariant:** Left subtree keys < Node key < Right subtree keys.

### F. Custom Data Structures (`structures.py`)
Three textbook structures are implemented from scratch:
- **`Vector`** — Dynamic Array with `push_back`, `linear_search` ($\mathcal{O}(N)$), and `binary_search` ($\mathcal{O}(\log N)$), capacity doubling on overflow.
- **`MinHeapPriorityQueue`** — Complete binary tree stored in a linear array; `push`/`pop` in $\mathcal{O}(\log N)$; used by Dijkstra.
- **`BinarySearchTree`** — Linked BST with iterative insert/search, and recursive delete (all 3 cases: leaf, single child, two children with in-order successor replacement).

---

## 4. Project Directory Structure

```
d:/DSA_PROJECT_WEB/
├── webtrace/
│   ├── __init__.py             # Package initializer
│   ├── app.py                  # Flask REST API + serves React frontend build
│   ├── crawler.py              # Main controller — BFS loop (Queue + Set + BST)
│   ├── fetcher.py              # HTTP GET, robots.txt check, politeness delay
│   ├── parser.py               # BeautifulSoup HTML link, title & content extractor
│   ├── url_utils.py            # URL normalization + same-domain filtering
│   ├── graph.py                # LinkGraph class (Adjacency List + Dijkstra)
│   ├── structures.py           # Custom DSA: Vector, MinHeapPriorityQueue, BST
│   ├── exporter.py             # Writes crawled_pages.csv and link_graph.json
│   ├── main.py                 # CLI entry point
│   ├── interactive.py          # Interactive terminal-based crawl interface
│   ├── demo_bfs.py             # In-memory BFS crawl simulation demo
│   ├── templates/              # Fallback HTML templates (when React build absent)
│   ├── tests/
│   │   ├── test_url_utils.py       # Tricky URL normalization & domain tests
│   │   ├── test_graph.py           # Adjacency list & edge deduplication tests
│   │   ├── test_crawler_bfs.py     # BFS level-order & cycle avoidance tests
│   │   ├── test_fetcher.py         # HTTP, robots.txt & politeness tests
│   │   ├── test_parser.py          # HTML parsing tests
│   │   ├── test_exporter.py        # CSV & JSON export validation tests
│   │   ├── test_app.py             # Flask API endpoint tests
│   │   └── test_syllabus_dsa.py    # Vector, MinHeap & BST correctness tests
│   └── output/
│       ├── crawled_pages.csv       # BFS traversal metadata export
│       └── link_graph.json         # Adjacency list JSON export
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Root React component (tabs, theme, state)
│   │   ├── main.jsx                # React entry point
│   │   ├── index.css               # Global styles
│   │   └── components/
│   │       ├── Navbar.jsx          # Top navigation bar with theme toggle
│   │       ├── CrawlForm.jsx       # Crawl configuration form
│   │       ├── StatCards.jsx       # Live crawl statistics cards
│   │       ├── PagesTable.jsx      # Tabular BFS traversal results
│   │       ├── ContentsView.jsx    # Extracted page content viewer
│   │       ├── NetworkGraph.jsx    # Interactive vis-network node-link graph
│   │       ├── JsonViewer.jsx      # Raw JSON adjacency list viewer
│   │       └── DsaExplainer.jsx    # In-app DSA concept explainer panel
│   ├── dist/                       # Compiled React production build (served by Flask)
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── README.md                       # Project documentation & DSA concept mapping
├── requirements.txt                # Python dependencies
└── WebTrace_Presentation.html      # Project presentation slides
```

---

## 5. Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm (for frontend development)
- `pip`

### Install Python Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies: `requests`, `beautifulsoup4`, `pytest`, `flask`)*

### Install Frontend Dependencies (optional — only for UI development)
```bash
cd frontend
npm install
```

---

## 6. How to Run

### Option 1: Unified Python Server *(Recommended)*
Run the Flask backend, which automatically serves the compiled React + Tailwind frontend from `frontend/dist/`:
```bash
# From the project root:
python -m webtrace.app

# Or from inside the webtrace folder:
python webtrace/app.py

# With custom host/port:
python -m webtrace.app --host 0.0.0.0 --port 8080
```
- Open **`http://127.0.0.1:5000`** in your browser.

---

### Option 2: React + Vite Development Server (with Hot Reloading)
For live frontend development with instant HMR:

1. In Terminal 1, start the Python API server:
   ```bash
   python webtrace/app.py
   ```
2. In Terminal 2, start the Vite development server:
   ```bash
   cd frontend
   npm run dev
   ```
- Open **`http://localhost:5173`** in your browser. All API requests (`/api/*`) are automatically proxied to the Python backend on port 5000.

To build the frontend for production:
```bash
cd frontend
npm run build
```

---

### Option 3: Interactive Terminal Prompts
Run in interactive console mode without a browser:
```bash
python -m webtrace.interactive
```

---

### Option 4: Command-Line Interface (CLI)
```bash
# Basic crawl
python -m webtrace.main --seed https://example.com/ --max-depth 2 --max-pages 10

# Dry-run simulation (no network requests)
python -m webtrace.main --seed https://example.com/ --dry-run
```

### Advanced CLI Options
```bash
python -m webtrace.main \
  --seed https://example.com/ \
  --max-depth 3 \
  --max-pages 25 \
  --delay 1.5 \
  --timeout 5.0 \
  --output-dir output \
  --verbose
```

#### CLI Arguments Reference:
- `--seed`: Starting URL for crawl (default: `https://example.com/`)
- `--max-depth`: Maximum BFS hop distance (default: `2`)
- `--max-pages`: Maximum pages to crawl (default: `10`)
- `--delay`: Politeness delay between requests to same domain in seconds (default: `1.0`)
- `--timeout`: HTTP timeout in seconds (default: `5.0`)
- `--output-dir`: Output directory for exports (default: `webtrace/output`)
- `--dry-run`: Simulate crawl setup without network requests
- `--no-robots`: Bypass `robots.txt` compliance (not recommended)
- `--verbose`: Enable DEBUG logging
- `--quiet`: Suppress informational messages

---

## 7. REST API Reference

The Flask backend exposes the following API endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/crawl` | Run a BFS crawl and return pages, graph, and statistics |
| `GET` | `/api/download/csv` | Download the last crawl as `crawled_pages.csv` |
| `GET` | `/api/download/json` | Download the last crawl graph as `link_graph.json` |
| `POST` | `/api/graph/shortest-path` | Compute shortest path between two URLs (Dijkstra) |
| `GET` | `/api/pages/bst-inorder` | Return crawled pages sorted by BST In-Order traversal |

### `POST /api/crawl` — Request Body
```json
{
  "seed": "https://quotes.toscrape.com/",
  "max_depth": 2,
  "max_pages": 15,
  "delay": 0.5,
  "respect_robots": true,
  "dry_run": false
}
```

### `POST /api/graph/shortest-path` — Request Body
```json
{
  "start_url": "https://quotes.toscrape.com/",
  "target_url": "https://quotes.toscrape.com/page/3/"
}
```

---

## 8. Frontend UI Overview

The React dashboard provides the following tabs and panels:

| Panel | Component | Description |
|---|---|---|
| **Crawl Form** | `CrawlForm.jsx` | Seed URL input, depth/pages/delay controls, robots.txt toggle, dry-run mode |
| **Statistics** | `StatCards.jsx` | Live counters: pages crawled, graph nodes/edges, text blocks, documents, URLs, elapsed time |
| **Pages Table** | `PagesTable.jsx` | BFS traversal table with URL, title, depth, parent, outgoing links, and search/filter |
| **Contents View** | `ContentsView.jsx` | Per-page content viewer: text blocks, extracted documents, all discovered URLs |
| **Network Graph** | `NetworkGraph.jsx` | Interactive `vis-network` node-link graph; shortest-path query UI |
| **JSON Viewer** | `JsonViewer.jsx` | Raw adjacency list JSON explorer |
| **DSA Explainer** | `DsaExplainer.jsx` | Slide-out panel explaining BFS, Dijkstra, BST, and Min-Heap concepts |

Additional features:
- **Dark / Light theme** toggle with `localStorage` persistence.
- **Download** buttons for CSV and JSON exports from the dashboard.

---

## 9. Running the Test Suite

Run the full automated test suite using `pytest`:

```bash
python -m pytest -v
```

Run specific test modules:
```bash
python -m pytest webtrace/tests/test_url_utils.py -v
python -m pytest webtrace/tests/test_crawler_bfs.py -v
python -m pytest webtrace/tests/test_fetcher.py -v
python -m pytest webtrace/tests/test_graph.py -v
python -m pytest webtrace/tests/test_syllabus_dsa.py -v   # Vector, MinHeap, BST
python -m pytest webtrace/tests/test_app.py -v             # Flask API endpoints
```

Run the standalone in-memory BFS simulation:
```bash
python -m webtrace.demo_bfs
```

---

## 10. Sample Export Outputs

### CSV Output (`output/crawled_pages.csv`)
```csv
URL,Title,Depth,Parent URL,Outgoing Links
https://example.com/,Example Domain,0,—,0
https://example.com/about,About Us,1,https://example.com/,3
https://example.com/contact,Contact Us,1,https://example.com/,1
```

### JSON Output (`output/link_graph.json`)
```json
{
  "https://example.com/": [
    "https://example.com/about",
    "https://example.com/contact"
  ],
  "https://example.com/about": [
    "https://example.com/"
  ],
  "https://example.com/contact": []
}
```

---

## 11. Algorithmic Complexity

| Operation / Step | Data Structure | Time Complexity | Space Complexity |
|---|---|---|---|
| Enqueue / Dequeue URL | Queue (`collections.deque`) | $\mathcal{O}(1)$ | $\mathcal{O}(|V|)$ |
| Visited Check & Insertion | Hash Set (`set`) | $\mathcal{O}(1)$ average | $\mathcal{O}(|V|)$ |
| Query / Insert Edge | Adjacency List (`dict[str, list]`) | $\mathcal{O}(1)$ average | $\mathcal{O}(|V| + |E|)$ |
| robots.txt / Politeness Lookup | Hash Map (`dict`) | $\mathcal{O}(1)$ average | $\mathcal{O}(\text{Domains})$ |
| BST Insert / Search | Binary Search Tree | $\mathcal{O}(\log N)$ average | $\mathcal{O}(|V|)$ |
| Min-Heap Push / Pop | Binary Min-Heap | $\mathcal{O}(\log N)$ | $\mathcal{O}(|V|)$ |
| Shortest Path | Dijkstra's Algorithm | $\mathcal{O}((|V| + |E|) \log |V|)$ | $\mathcal{O}(|V|)$ |
| BST In-Order Traversal | Binary Search Tree | $\mathcal{O}(|V|)$ | $\mathcal{O}(|V|)$ |
| Vector Binary Search | Dynamic Array | $\mathcal{O}(\log N)$ | $\mathcal{O}(1)$ |
| **Overall Crawl Execution** | **Graph BFS** | $\mathcal{O}(|V| + |E|)$ | $\mathcal{O}(|V| + |E|)$ |

---

## 12. License & Academic Integrity

This project is submitted as coursework for **ECE 2103 (Data Structures & Algorithms)**. It complies with ethical web scraping guidelines by strictly enforcing domain boundaries, politeness delays, and the Robots Exclusion Standard (`robots.txt`).
