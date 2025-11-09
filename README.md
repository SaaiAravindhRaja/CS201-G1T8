# CS201 Data Structures and Algorithms — Team G1T8

## Skytrax User Reviews Dataset Analysis

---

## Team G1T8 Members

<table align="center">
	<tr>
		<td align="center">
			<a href="https://github.com/SaaiAravindhRaja">
				<img src="https://github.com/SaaiAravindhRaja.png" width="80" alt="SaaiAravindhRaja"/><br/>
				<sub><b>SaaiAravindhRaja</b></sub><br/>
				<sub>Saai</sub>
			</a>
		</td>
		<td align="center">
			<a href="https://github.com/Onyxxx17">
				<img src="https://github.com/Onyxxx17.png" width="80" alt="Onyxxx17"/><br/>
				<sub><b>Onyxxx17</b></sub><br/>
				<sub>Aung</sub>
			</a>
		</td>
		<td align="center">
			<a href="https://github.com/regan-tan">
				<img src="https://github.com/regan-tan.png" width="80" alt="regan-tan"/><br/>
				<sub><b>regan-tan</b></sub><br/>
				<sub>Regan</sub>
			</a>
		</td>
		<td align="center">
			<a href="https://github.com/chuems">
				<img src="https://github.com/chuems.png" width="80" alt="chuems"/><br/>
				<sub><b>chuems</b></sub><br/>
				<sub>Chue</sub>
			</a>
		</td>
		<td align="center">
			<a href="https://github.com/thanh913">
				<img src="https://github.com/thanh913.png" width="80" alt="thanh913"/><br/>
				<sub><b>thanh913</b></sub><br/>
				<sub>Billy</sub>
			</a>
		</td>
	</tr>
</table>

---

## Overview

This repository is a comprehensive sandbox for exploring and benchmarking substring-search data structures on the Skytrax review datasets (airline, airport, lounge, seat). The project implements five different search algorithms and provides tools for interactive querying and performance analysis.

The architecture consists of three main components:

- **Search Algorithms (`src/indexes/`)** – Five implementations of substring matching: KMP (Knuth-Morris-Pratt), K-Gram Index, Suffix Array (two variants), and Aho-Corasick, all implementing a common `Matcher` interface.
- **Interactive CLI (`scripts/cli.py`)** – A feature-rich REPL for loading datasets, selecting search backends, and running multi-pattern AND/OR queries with detailed performance metrics.
- **Benchmarking Suite (`scripts/run_benchmarks.py`, `scripts/plot_from_log.py`)** – Automated tools for measuring build times, query performance, and memory usage across varying corpus sizes, with visualization support.

---

## Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (includes matplotlib for plotting)
pip install -r requirements.txt
```

The datasets are pre-loaded in `data/raw/` with four CSV files:
- `airline.csv` - Airline reviews
- `airport.csv` - Airport reviews  
- `lounge.csv` - Lounge reviews
- `seat.csv` - Seat reviews

Each CSV row is indexed with a unique document ID format: `<dataset>:<row_number>` (e.g., `airline:123`).

---

## Interactive CLI

The CLI provides a powerful interface for exploring different search algorithms and comparing their performance on real datasets.

### Starting the CLI

```bash
python scripts/cli.py
```

You'll be greeted with an interactive prompt. Type `help` to see all available commands.

### Available Commands

#### 1. Algorithm Information

```bash
# View comparison of all algorithms
info

# Get detailed information about a specific algorithm
info ac
info kmp
info sa
info salog2
info kgram
```

This displays complexity analysis, best use cases, and implementation details for each algorithm.

#### 2. Loading a Backend

```bash
backend <algorithm> <dataset> [limit]
```

Loads and builds an index on the specified dataset.

Parameters:
- `algorithm`: Choose from `kmp`, `ac`, `sa`, `salog2`, or `kgram`
- `dataset`: Choose from `airline`, `airport`, `lounge`, or `seat`
- `limit`: Optional, number of documents to load (default: 50000)

Examples:
```bash
# Load 1000 airline reviews using Aho-Corasick
backend ac airline 1000

# Load 5000 airport reviews using Suffix Array
backend sa airport 5000

# Load all available lounge reviews using K-Gram
backend kgram lounge
```

The CLI will display:
- Build time in seconds
- Number of documents loaded
- Memory usage during build
- Algorithm details

#### 3. Searching

```bash
query --patterns "pattern1,pattern2,..." --mode <and|or> [--show-text]
```

Executes a multi-pattern search on the loaded dataset.

Parameters:
- `--patterns`: Comma-separated list of search terms (case-insensitive)
- `--mode`: 
  - `and` - Returns documents containing ALL patterns
  - `or` - Returns documents containing ANY pattern
- `--show-text`: Optional flag to display matching document text (first 150 chars)

Examples:
```bash
# Find reviews mentioning both "wifi" and "free"
query --patterns "wifi,free" --mode and

# Find reviews mentioning either "delay" or "cancelled"
query --patterns "delay,cancelled" --mode or

# Search with text preview
query --patterns "comfortable,seat" --mode and --show-text
```

Query results include:
- Algorithm used
- Build time (from backend loading)
- Query execution time in milliseconds
- Number of matching documents
- Document IDs (first 20 shown)
- Optional: Document text preview

#### 4. Status Check

```bash
status
```

Displays current CLI state:
- Active backend algorithm
- Loaded dataset name
- Number of documents indexed
- Build time
- Ready status

#### 5. Algorithm Comparison

```bash
compare --patterns "pattern1,pattern2" --mode <and|or>
```

Runs the same query across ALL five algorithms and displays a performance comparison table.

Example:
```bash
compare --patterns "leg,comfort" --mode and
```

Output includes:
- Build time for each algorithm
- Query time for each algorithm
- Number of matches (should be identical across all)
- Fastest algorithm highlighted

This is extremely useful for understanding which algorithm performs best for your specific query patterns and corpus size.

### Algorithm Details

The CLI provides detailed information about each algorithm:

**KMP (Knuth-Morris-Pratt)**
- Linear-time string matching using failure function
- Complexity: O(n+m) per query | O(n) space
- Best for: Single pattern searches, guaranteed linear time

**Aho-Corasick**
- Trie-based multi-pattern matching with failure links
- Complexity: O(n+m+z) where z=matches | O(alphabet×states) space
- Best for: Multiple patterns simultaneously (AND/OR queries)

**K-Gram Index**
- Character-level inverted index (k=3 substrings)
- Complexity: O(k) lookup + O(candidates) verification | O(vocabulary×docs) space
- Best for: Fuzzy/substring search with moderate corpus size

**Suffix Array**
- Sorted array of all text suffixes with binary search
- Complexity: O(m log n) query | O(n) build, O(n) space
- Best for: Substring queries after one-time O(n log n) build

**Suffix Array + LCP**
- Enhanced suffix array with Longest Common Prefix
- Complexity: O(m + log n) query | O(n) space with LCP array
- Best for: Repeated substring queries with better constants

### Example CLI Session

```bash
$ python scripts/cli.py

================================================================================
                        CS201 SUBSTRING SEARCH CLI
================================================================================

💡 Type 'help' for commands or 'info' for algorithm comparison

> info ac

================================================================================
                              Aho-Corasick
================================================================================

📝 Description: Trie-based multi-pattern matching with failure links
⚡ Complexity:   O(n+m+z) where z=matches | O(alphabet×states) space
✅ Best for:     Multiple patterns simultaneously (e.g., AND/OR queries)

================================================================================

> backend ac airline 1000

🔨 Building Aho-Corasick...
📊 Dataset: airline | Limit: 1000 documents
Loaded 1000 records successfully.    

✅ Backend ready!
   Algorithm: Aho-Corasick
   Dataset: airline
   Documents: 1,000
   Build time: 0.234s

💡 Next: query --patterns "wifi,delay" --mode and

[AC | airline | 1000 docs]> query --patterns "comfortable,seat" --mode and

🔍 Searching with Aho-Corasick...
   Patterns: ['comfortable', 'seat']
   Mode: AND

📊 RESULTS:
   Algorithm: AC
   Build time: 0.234s
   Query time: 2.456ms
   Matches: 47 documents

📋 DOCUMENT IDs (showing first 20):
   • airline:12
   • airline:45
   • airline:89
   ...

💡 Run another query or type 'exit' to quit

[AC | airline | 1000 docs]> compare --patterns "comfortable,seat" --mode and

🔬 BENCHMARK: Comparing all backends
   Documents: 1,000
   Patterns: ['comfortable', 'seat']
   Mode: AND

   Testing KMP (Knuth-Morris-Pratt)...                     ✓
   Testing Aho-Corasick...                                 ✓
   Testing Suffix Array...                                 ✓
   Testing Suffix Array + LCP...                           ✓
   Testing K-Gram Index...                                 ✓

Algorithm                 Build (s)    Query (ms)   Matches   
-----------------------------------------------------------------
KMP (Knuth-Morris-Pratt)  0.156        8.234        47        
Aho-Corasick              0.234        2.456        47        
Suffix Array              0.445        1.123        47        
Suffix Array + LCP        0.512        0.987        47        
K-Gram Index              0.389        3.567        47        

🏆 Fastest query: Suffix Array + LCP (0.987ms)

[AC | airline | 1000 docs]> exit

👋 Goodbye!
```

---

## Benchmarking Suite

The benchmarking tools allow you to systematically measure and compare algorithm performance across different corpus sizes.

### Running Benchmarks

#### Automated Benchmark Script

```bash
python scripts/run_benchmarks.py --output-dir benchmark_output
```

This script:
1. Loads the airline dataset
2. Tests all five algorithms at corpus sizes: [100, 500, 1000, 5000, 10000]
3. Measures for each algorithm:
   - Build time (seconds)
   - Peak memory usage (MiB)
   - Query time for multiple query types (milliseconds)
4. Generates CSV summary and PNG plots

Query types tested:
- `substr_short`: Short substring query ("leg")
- `substr_medium`: Medium substring query ("comfort")
- `prefix`: Prefix query ("seat")
- `or_substr`: Multi-pattern OR query ("leg comf")

Output files:
- `benchmark_output/benchmark_summary.csv` - Raw data in CSV format
- `benchmark_output/build_time.png` - Build time comparison
- `benchmark_output/substr_short_query.png` - Short query performance
- `benchmark_output/substr_medium_query.png` - Medium query performance
- `benchmark_output/prefix_query.png` - Prefix query performance
- `benchmark_output/or_substr_query.png` - OR query performance

#### Plotting from Log Files

If you have textual benchmark output (e.g., from console logs), you can generate plots:

```bash
python scripts/plot_from_log.py --input results.txt --output-dir benchmark_graphs
```

Expected log format:
```
Limit 100 docs
  AhoCorasick  build 0.000s | peak 0.1 MiB | substr_short:0.061ms, substr_medium:0.039ms
  KGram        build 0.034s | peak 2.8 MiB | substr_short:0.066ms, substr_medium:0.041ms
  ...

Limit 500 docs
  AhoCorasick  build 0.002s | peak 0.5 MiB | substr_short:0.234ms, substr_medium:0.189ms
  ...
```

The script parses this format and generates the same set of plots as the automated benchmark.

### Understanding Benchmark Results

The generated plots help you understand:

1. **Build Time vs Corpus Size** (`build_time.png`)
   - Shows how index construction time scales with document count
   - Suffix arrays typically have higher build times but better query performance
   - KMP and Aho-Corasick have minimal build overhead

2. **Memory Usage** (`memory_peak.png`)
   - Peak memory consumption during index construction
   - K-Gram typically uses more memory due to inverted index
   - Suffix arrays are memory-efficient despite their power

3. **Query Performance** (various `*_query.png` files)
   - Query execution time for different pattern types
   - Aho-Corasick excels at multi-pattern queries
   - Suffix arrays show consistent performance across query types
   - KMP may be slower for large corpora but has predictable behavior

### Benchmark Workflow

For comprehensive analysis:

```bash
# 1. Run automated benchmarks
python scripts/run_benchmarks.py --output-dir my_results

# 2. Check the CSV for raw data
cat my_results/benchmark_summary.csv

# 3. View generated plots
open my_results/*.png

# 4. If you have additional log files, parse them
python scripts/plot_from_log.py --input custom_log.txt --output-dir my_results
```

### Interpreting Results

When choosing an algorithm, consider:

- **Small datasets (<1000 docs)**: KMP or Aho-Corasick for minimal build time
- **Medium datasets (1000-10000 docs)**: Aho-Corasick for multi-pattern, Suffix Array for repeated queries
- **Large datasets (>10000 docs)**: Suffix Array variants for best query performance
- **Multi-pattern queries**: Aho-Corasick is specifically optimized for this
- **Memory-constrained environments**: KMP or basic Suffix Array
- **Fuzzy/partial matching**: K-Gram Index

---

## Project Structure

```
.
├── data/
│   └── raw/                    # CSV datasets
│       ├── airline.csv         # Airline reviews
│       ├── airport.csv         # Airport reviews
│       ├── lounge.csv          # Lounge reviews
│       └── seat.csv            # Seat reviews
│
├── src/
│   ├── indexes/                # Search algorithm implementations
│   │   ├── base.py            # Matcher interface
│   │   ├── kmp.py             # KMP algorithm (not shown but implied)
│   │   ├── aho_corasick.py    # Aho-Corasick algorithm
│   │   ├── kgram_index.py     # K-Gram inverted index
│   │   ├── suffix_array.py    # Basic suffix array
│   │   └── suffix_array_logsq.py  # Enhanced suffix array with LCP
│   ├── corpus.py              # Dataset loading utilities
│   ├── engine.py              # SearchEngine wrapper
│   └── text_utils.py          # String processing helpers
│
├── scripts/
│   ├── cli.py                 # Interactive CLI (main interface)
│   ├── run_benchmarks.py      # Automated benchmark suite
│   └── plot_from_log.py       # Log parsing and visualization
│
├── benchmark_graphs/          # Pre-generated benchmark plots
│   ├── build_time.png
│   ├── memory_peak.png
│   ├── substr_short_query.png
│   ├── substr_medium_query.png
│   ├── prefix_query.png
│   └── or_substr_query.png
│
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Development Tips

The repository is designed to be easily hackable:

1. **Adding new algorithms**: Implement the `Matcher` interface in `src/indexes/base.py`
2. **Custom queries**: Modify the `QUERIES` list in `scripts/run_benchmarks.py`
3. **Different datasets**: Add CSV files to `data/raw/` and update `DATASETS` in `cli.py`
4. **Visualization**: Customize plot styles in `scripts/plot_from_log.py`

All algorithms share a common interface, making it easy to swap implementations and compare results.

---
