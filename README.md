# WebTrace: Domain-Restricted BFS Web Crawler

> **Course:** ECE 2103 — Data Structures & Algorithms  
> **Category:** DSA Course Project  
> **Language:** Python 3  

---

## 1. Project Overview

**WebTrace** is a domain-restricted web crawler designed as an educational teaching artifact for Data Structures and Algorithms (DSA). Starting from a single seed URL, WebTrace systematically crawls web pages within the same domain using **Breadth-First Search (BFS)** traversal, builds a directed **Link Graph** representing the website's structure, respects the `robots.txt` protocol and politeness rate limits, and exports structured results to **CSV** and **JSON**.

---

## 2. DSA Concept Mapping

Every module in WebTrace is designed to explicitly demonstrate core Data Structures and Algorithms topics taught in the ECE 2103 syllabus:

| Module | Responsibility | Key Data Structure / Algorithm | Syllabus Topic |
|---|---|---|---|
| [`webtrace/crawler.py`](webtrace/crawler.py) | Orchestrates the BFS traversal loop; controls crawl frontier and visit tracking. | **FIFO Queue** (`collections.deque`), **Visited Set** (`set`) | **Queue (FIFO)**, **Hash Set**, **Breadth-First Search (BFS)** |
| [`webtrace/graph.py`](webtrace/graph.py) | Models and stores the website's hyperlink topology. | **Adjacency List** (`dict[str, list[str]]`) | **Graph Representation (Adjacency List vs Matrix)** |
| [`webtrace/url_utils.py`](webtrace/url_utils.py) | URL canonicalization, fragment stripping, and domain restriction. | **String Parsing**, **Canonical Hashing Invariant** | **Hashing & Collision Invariants** |
| [`webtrace/fetcher.py`](webtrace/fetcher.py) | Network I/O, `robots.txt` compliance, and politeness rate-limiting. | **Hash Map Caching** (`dict[str, RobotFileParser]`, `dict[str, float]`) | **Hash Tables (Caching & State Tracking)** |
| [`webtrace/parser.py`](webtrace/parser.py) | Extracts `<title>` and `<a href="...">` links from HTML. | **String Parsing / DOM Tokenization** | **String & Tree Parsing** |
| [`webtrace/exporter.py`](webtrace/exporter.py) | Serializes traversal search tree and adjacency list to disk. | **Tabular Serialization** (CSV) & **Graph Serialization** (JSON) | **Data Structure Serialization** |
| [`webtrace/main.py`](webtrace/main.py) | CLI driver and argument parser. | **Application Driver** | **System Orchestration** |

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

---

## 4. Project Directory Structure

```
d:/DSA_PROJECT_WEB/
├── webtrace/
│   ├── __init__.py           # Package initializer
│   ├── crawler.py            # Main controller — BFS loop (Queue + Set)
│   ├── fetcher.py            # HTTP GET, robots.txt check, politeness delay
│   ├── parser.py             # BeautifulSoup HTML link & title extractor
│   ├── url_utils.py          # URL normalization + same-domain filtering
│   ├── graph.py              # LinkGraph class (Adjacency List)
│   ├── exporter.py           # Writes crawled_pages.csv and link_graph.json
│   ├── main.py               # CLI entry point
│   ├── demo_bfs.py           # In-memory BFS crawl simulation demo
│   ├── tests/
│   │   ├── test_url_utils.py   # Tricky URL normalization & domain tests
│   │   ├── test_graph.py       # Adjacency list & edge deduplication tests
│   │   ├── test_crawler_bfs.py # BFS level-order & cycle avoidance tests
│   │   ├── test_fetcher.py     # HTTP, robots.txt & politeness tests
│   │   ├── test_parser.py      # HTML parsing tests
│   │   └── test_exporter.py    # CSV & JSON export validation tests
│   └── output/
│       ├── crawled_pages.csv   # BFS traversal metadata export
│       └── link_graph.json     # Adjacency list JSON export
├── README.md                 # Project documentation & DSA concept mapping
└── requirements.txt          # Project dependencies
```

---

## 5. Setup & Installation

### Prerequisites
- Python 3.10+
- `pip`

### Install Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies: `requests`, `beautifulsoup4`, `pytest`)*

---

## 6. How to Run

### Option 1: Unified Python Server (Serves React Production Build)
Run the Python backend server directly. It automatically serves the compiled React + Tailwind frontend:
```bash
# From inside the webtrace folder:
python app.py

# Or from the project root:
python -m webtrace.app
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

## 7. Running the Test Suite

Run the full automated test suite using `pytest`:

```bash
python -m pytest -v
```

Run specific test modules:
```bash
python -m pytest webtrace/tests/test_url_utils.py -v
python -m pytest webtrace/tests/test_crawler_bfs.py -v
python -m pytest webtrace/tests/test_fetcher.py -v
```

Run the standalone in-memory BFS simulation:
```bash
python -m webtrace.demo_bfs
```

---

## 8. Sample Export Outputs

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

## 9. Algorithmic Complexity

| Operation / Step | Data Structure | Time Complexity | Space Complexity |
|---|---|---|---|
| Enqueue / Dequeue URL | Queue (`collections.deque`) | $\mathcal{O}(1)$ | $\mathcal{O}(|V|)$ |
| Visited Check & Insertion | Hash Set (`set`) | $\mathcal{O}(1)$ average | $\mathcal{O}(|V|)$ |
| Query / Insert Edge | Adjacency List (`dict[str, list]`) | $\mathcal{O}(1)$ average | $\mathcal{O}(|V| + |E|)$ |
| robots.txt / Politeness Lookup | Hash Map (`dict`) | $\mathcal{O}(1)$ average | $\mathcal{O}(\text{Domains})$ |
| **Overall Crawl Execution** | **Graph BFS** | $\mathcal{O}(|V| + |E|)$ | $\mathcal{O}(|V| + |E|)$ |

---

## 10. License & Academic Integrity

This project is submitted as coursework for **ECE 2103 (Data Structures & Algorithms)**. It complies with ethical web scraping guidelines by strictly enforcing domain boundaries, politeness delays, and the Robots Exclusion Standard (`robots.txt`).
