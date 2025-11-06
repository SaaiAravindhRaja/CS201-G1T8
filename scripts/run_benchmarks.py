#!/usr/bin/env python3
"""Benchmark search indices across increasing corpus sizes and plot results."""

from __future__ import annotations

import argparse
import csv
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError as exc:  # pragma: no cover
    plt = None
    print("Warning: matplotlib missing; plots will not be generated.", file=sys.stderr)

from src import SearchEngine
import inspect

from src import indexes as indexes_module
from src.indexes.base import Index as IndexBase
from src.corpus import iter_reviews_from_csv

DATA_CSV = Path("data/raw/airline.csv")
SOURCE_TAG = "airline"
DEFAULT_OUTPUT = Path("benchmark_output")

def discover_indexes():
    factories = {}
    for name in dir(indexes_module):
        attr = getattr(indexes_module, name)
        if inspect.isclass(attr) and issubclass(attr, IndexBase) and attr is not IndexBase:
            factories[name] = attr
    if not factories:
        raise RuntimeError("No index implementations found in src.indexes")
    return factories

QUERIES: Sequence[Tuple[str, str, str]] = [
    ("single", "legroom", "and"),
    ("and_terms", "legroom comfortable", "and"),
    ("or_terms", "legroom spacious", "or"),
]


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark indices over varying corpus sizes.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for plots and CSV (default: benchmark_output).",
    )
    return parser.parse_args(list(argv))


def load_all_records() -> List[Tuple[str, str]]:
    return list(iter_reviews_from_csv(DATA_CSV, source_tag=SOURCE_TAG))


CORPUS_SIZES = [100, 500, 1000, 5000, 10000]


def build_engine(factory, records: Sequence[Tuple[str, str]]) -> Tuple[SearchEngine, float, float]:
    tracemalloc.start()
    engine = SearchEngine(factory())
    start = time.perf_counter()
    for doc_id, text in records:
        engine.add_document(doc_id, text)
    build_time = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return engine, build_time, peak / (1024 * 1024)


def measure_queries(engine: SearchEngine) -> Dict[str, float]:
    timings: Dict[str, float] = {}
    for label, query, mode in QUERIES:
        start = time.perf_counter()
        engine.search(query, match_mode=mode)
        timings[label] = (time.perf_counter() - start) * 1000.0  # ms
    return timings


def write_csv(path: Path, rows: List[Dict[str, float]]) -> None:
    fieldnames = [
        "limit",
        "index",
        "build_time_s",
        "peak_memory_mib",
        *[f"{label}_ms" for label, _, _ in QUERIES],
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def plot_results(output_dir: Path, rows: List[Dict[str, float]], index_names: Sequence[str]) -> None:
    if plt is None:
        print("Skipping plots because matplotlib is unavailable.", file=sys.stderr)
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    limits = sorted({int(row["limit"]) for row in rows})

    # Build time plot
    plt.figure(figsize=(8, 5))
    for index_name in index_names:
        times = [row["build_time_s"] for row in rows if row["index"] == index_name]
        plt.plot(limits, times, marker="o", label=index_name)
    plt.xlabel("Documents indexed")
    plt.ylabel("Build time (s)")
    plt.title("Index Build Time vs Corpus Size")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "build_time.png")
    plt.close()

    # Query time plots
    for label, _, _ in QUERIES:
        plt.figure(figsize=(8, 5))
        for index_name in index_names:
            times = [row[f"{label}_ms"] for row in rows if row["index"] == index_name]
            plt.plot(limits, times, marker="o", label=index_name)
        plt.xlabel("Documents indexed")
        plt.ylabel("Query time (ms)")
        plt.title(f"Query '{label}' Performance")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"{label}_query.png")
        plt.close()


def main(argv: Iterable[str]) -> None:
    args = parse_args(argv)
    output_dir = args.output_dir
    records = load_all_records()
    total_docs = len(records)
    limits = [size for size in CORPUS_SIZES if size <= total_docs]
    if not limits or limits[-1] < total_docs:
        limits.append(total_docs)
    index_factories = discover_indexes()
    ordered_names = sorted(index_factories.keys())
    print(f"Benchmarking {len(limits)} corpus sizes: {limits}")

    rows: List[Dict[str, float]] = []
    for limit in limits:
        subset = records[:limit]
        print(f"\nLimit {limit} docs")
        for index_name in ordered_names:
            factory = index_factories[index_name]
            engine, build_time, peak_mem = build_engine(factory, subset)
            query_timings = measure_queries(engine)
            row = {
                "limit": float(limit),
                "index": index_name,
                "build_time_s": build_time,
                "peak_memory_mib": peak_mem,
            }
            for label in [q[0] for q in QUERIES]:
                row[f"{label}_ms"] = query_timings[label]
            rows.append(row)
            print(
                f"  {index_name:12s} build {build_time:.3f}s | peak {peak_mem:.1f} MiB | "
                + ", ".join(f"{label}:{query_timings[label]:.3f}ms" for label in query_timings)
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "benchmark_summary.csv"
    write_csv(csv_path, rows)
    plot_results(output_dir, rows, ordered_names)
    print(f"\nResults saved in {output_dir}")


if __name__ == "__main__":
    main(sys.argv[1:])
