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

This repo is now a lightweight sandbox for substring-search data structures on the Skytrax review datasets (airline, airport, lounge, seat). Everything revolves around three pieces:

- **Matchers (`src/indexes`)** – KMP, K-Gram, two suffix-array variants, and Aho–Corasick implementing a common `Matcher` interface.
- **CLI (`scripts/cli.py`)** – a tiny REPL that loads a dataset, picks a backend, and runs multi-pattern AND/OR searches across *all* reviews, printing timings and doc IDs (with optional review text).
- **Benchmarks (`scripts/run_*.py`, `scripts/plot_from_log.py`)** – helpers to sweep corpus sizes, capture logs, and turn them into plots (see `benchmark_graphs/`).

The old academic report/tests were deliberately removed so the code stays focused and hackable.

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Datasets already live in `data/raw/`; each CSV row becomes a document id like `airline:123`.

---

## CLI (scripts/cli.py)

```bash
python scripts/cli.py
```

Commands (in order):

1. `backend <kmp|ac|sa|salog2|kgram> <dataset> [limit]`
   - Builds the backend on the first `limit` reviews of the dataset (`airline`, `airport`, `lounge`, `seat`).
2. `query --patterns "leg,comfort,meal" --mode or [--show-text]`
   - Runs a multi-pattern AND/OR search across *all* loaded reviews.
   - `--show-text` also prints the raw review text for each matching doc id.
3. `help`, `exit`

Each query prints build/query timings and the number of matched reviews, so you can feel when Aho–Corasick overtakes KMP or when suffix arrays become worthwhile.

---

## Benchmarks & Plots

- `scripts/run_benchmarks.py`, `scripts/enhanced_benchmarks.py`, `scripts/run_sa_benchmarks.py` sweep corpus sizes and log build/query stats for every matcher.
- `scripts/plot_from_log.py --input results.txt --output-dir benchmark_graphs` parses textual logs (like `benchmark_results_from_user.txt`) into PNG charts.
- Latest plots are versioned in `benchmark_graphs/` for quick reference.

---

## Directory Highlights

```
src/
  indexes/        # matcher implementations
  corpus.py       # iter_reviews_from_csv helper
  text_utils.py   # shared substring helpers
scripts/
  cli.py, search_doc.py   # interactive tools
  run_*.py, plot_from_log # benchmarking workflow
benchmark_graphs/         # generated charts
```

Hack away: swap backends, tweak datasets, add new experiments—the repo is intentionally small and easy to modify.

---
