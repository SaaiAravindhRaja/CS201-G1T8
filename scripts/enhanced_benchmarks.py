#!/usr/bin/env python3
"""Enhanced benchmark with proper memory measurement and growth rate analysis."""

from __future__ import annotations

import argparse
import csv
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError as exc:
    plt = None
    print("Warning: matplotlib missing; plots will not be generated.", file=sys.stderr)

from src import SearchEngine
import inspect

from src import indexes as indexes_module
from src.indexes.base import Index as IndexBase
from src.corpus import iter_reviews_from_csv

DATA_CSV = Path("data/raw/airline.csv")
SOURCE_TAG = "airline"
DEFAULT_OUTPUT = Path("benchmark_results")


def get_deep_size(obj, seen=None):
    """Recursively calculate actual memory size of object in bytes."""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    
    seen.add(obj_id)
    
    if isinstance(obj, dict):
        size += sum([get_deep_size(v, seen) for v in obj.values()])
        size += sum([get_deep_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_deep_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        try:
            size += sum([get_deep_size(i, seen) for i in obj])
        except TypeError:
            pass
    
    return size


def measure_index_memory(index: IndexBase) -> float:
    """Measure actual index structure memory in MiB."""
    return get_deep_size(index) / (1024 * 1024)


def get_index_statistics(index: IndexBase) -> Dict[str, int]:
    """Extract statistics about the index structure."""
    stats = {
        'vocabulary_size': 0,
        'total_postings': 0,
        'avg_posting_length': 0
    }
    
    try:
        if hasattr(index, '_postings'):  # InvertedIndex
            stats['vocabulary_size'] = len(index._postings)
            stats['total_postings'] = sum(len(posting) for posting in index._postings.values())
            if stats['vocabulary_size'] > 0:
                stats['avg_posting_length'] = stats['total_postings'] / stats['vocabulary_size']
        elif hasattr(index, '_documents'):  # ArrayScanIndex
            stats['vocabulary_size'] = 0  # Not applicable
            stats['total_postings'] = sum(len(tokens) for tokens in index._documents.values())
        elif hasattr(index, '_root'):  # TrieIndex
            def count_nodes(node):
                if node is None:
                    return 0
                count = 1
                for child in node.children.values():
                    count += count_nodes(child)
                return count
            stats['vocabulary_size'] = count_nodes(index._root)
    except Exception as e:
        print(f"Warning: Could not extract statistics: {e}", file=sys.stderr)
    
    return stats


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
    parser = argparse.ArgumentParser(description="Enhanced benchmark with memory analysis.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for plots and CSV (default: benchmark_results).",
    )
    return parser.parse_args(list(argv))


def load_all_records() -> List[Tuple[str, str]]:
    return list(iter_reviews_from_csv(DATA_CSV, source_tag=SOURCE_TAG))


CORPUS_SIZES = [100, 500, 1000, 5000, 10000]


def build_engine(factory, records: Sequence[Tuple[str, str]]) -> Tuple[SearchEngine, float, float, float, Dict]:
    """Build engine and return (engine, build_time, peak_memory, actual_memory, stats)"""
    tracemalloc.start()
    engine = SearchEngine(factory())
    start = time.perf_counter()
    for doc_id, text in records:
        engine.add_document(doc_id, text)
    build_time = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Measure actual index structure memory
    actual_memory = measure_index_memory(engine._index)
    
    # Get index statistics
    stats = get_index_statistics(engine._index)
    
    return engine, build_time, peak / (1024 * 1024), actual_memory, stats


def measure_queries(engine: SearchEngine) -> Dict[str, Tuple[float, int]]:
    """Return dict of {label: (time_ms, result_count)}"""
    timings: Dict[str, Tuple[float, int]] = {}
    for label, query, mode in QUERIES:
        start = time.perf_counter()
        results = engine.search(query, match_mode=mode)
        elapsed = (time.perf_counter() - start) * 1000.0  # ms
        timings[label] = (elapsed, len(results))
    return timings


def write_csv(path: Path, rows: List[Dict]) -> None:
    if not rows:
        return
    
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def calculate_growth_rate(sizes: List[float], times: List[float]) -> float:
    """
    Fit data to y = a * x^b to find b (growth exponent).
    Uses log-log linear regression: log(y) = log(a) + b*log(x)
    """
    if len(sizes) < 2 or len(times) < 2:
        return 0.0
    
    log_sizes = np.log(sizes)
    log_times = np.log(times)
    
    # Linear regression on log-log scale
    coefficients = np.polyfit(log_sizes, log_times, 1)
    growth_exponent = coefficients[0]
    
    return growth_exponent


def plot_results(output_dir: Path, rows: List[Dict], index_names: Sequence[str]) -> None:
    if plt is None:
        print("Skipping plots because matplotlib is unavailable.", file=sys.stderr)
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    limits = sorted({int(row["corpus_size"]) for row in rows})

    # 1. Build time plot
    plt.figure(figsize=(10, 6))
    for index_name in index_names:
        times = [row["build_time_s"] for row in rows if row["index_name"] == index_name]
        plt.plot(limits, times, marker="o", label=index_name, linewidth=2)
    plt.xlabel("Number of Documents", fontsize=12)
    plt.ylabel("Build Time (seconds)", fontsize=12)
    plt.title("Index Build Time vs Corpus Size", fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "build_time.png", dpi=300)
    plt.close()

    # 2. Build time (log-log scale)
    plt.figure(figsize=(10, 6))
    for index_name in index_names:
        times = [row["build_time_s"] for row in rows if row["index_name"] == index_name]
        growth_rate = calculate_growth_rate(limits, times)
        plt.loglog(limits, times, marker="o", 
                   label=f"{index_name} (growth ≈ O(n^{growth_rate:.2f}))", linewidth=2)
    plt.xlabel("Number of Documents (log scale)", fontsize=12)
    plt.ylabel("Build Time (log scale)", fontsize=12)
    plt.title("Build Time Growth Rate Analysis", fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3, which="both")
    plt.tight_layout()
    plt.savefig(output_dir / "build_time_loglog.png", dpi=300)
    plt.close()

    # 3. Actual memory usage
    plt.figure(figsize=(10, 6))
    for index_name in index_names:
        memory = [row["index_memory_mib"] for row in rows if row["index_name"] == index_name]
        plt.plot(limits, memory, marker="s", label=index_name, linewidth=2)
    plt.xlabel("Number of Documents", fontsize=12)
    plt.ylabel("Index Memory (MiB)", fontsize=12)
    plt.title("Index Memory Usage vs Corpus Size", fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "memory_usage.png", dpi=300)
    plt.close()

    # 4. Query time plots (for each query type)
    for label, _, _ in QUERIES:
        plt.figure(figsize=(10, 6))
        for index_name in index_names:
            times = [row[f"{label}_time_ms"] for row in rows if row["index_name"] == index_name]
            plt.plot(limits, times, marker="o", label=index_name, linewidth=2)
        plt.xlabel("Number of Documents", fontsize=12)
        plt.ylabel("Query Time (ms)", fontsize=12)
        plt.title(f"Query '{label}' Performance", fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / f"{label}_query.png", dpi=300)
        plt.close()

    # 5. Query time (log-log scale) for single term
    plt.figure(figsize=(10, 6))
    for index_name in index_names:
        times = [row["single_time_ms"] for row in rows if row["index_name"] == index_name]
        if all(t > 0 for t in times):  # Only plot if all times are positive
            growth_rate = calculate_growth_rate(limits, times)
            plt.loglog(limits, times, marker="o", 
                       label=f"{index_name} (growth ≈ O(n^{growth_rate:.2f}))", linewidth=2)
    plt.xlabel("Number of Documents (log scale)", fontsize=12)
    plt.ylabel("Query Time (log scale)", fontsize=12)
    plt.title("Query Growth Rate Analysis (Single Term)", fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3, which="both")
    plt.tight_layout()
    plt.savefig(output_dir / "query_time_loglog.png", dpi=300)
    plt.close()

    # 6. Speedup comparison (relative to ArrayScan)
    plt.figure(figsize=(10, 6))
    baseline_name = "ArrayScanIndex"
    if baseline_name in index_names:
        baseline_times = [row["single_time_ms"] for row in rows if row["index_name"] == baseline_name]
        for index_name in index_names:
            if index_name == baseline_name:
                continue
            times = [row["single_time_ms"] for row in rows if row["index_name"] == index_name]
            speedups = [b / t if t > 0 else 0 for b, t in zip(baseline_times, times)]
            plt.plot(limits, speedups, marker="o", label=f"{index_name} vs {baseline_name}", linewidth=2)
        plt.xlabel("Number of Documents", fontsize=12)
        plt.ylabel("Speedup Factor", fontsize=12)
        plt.title("Query Speedup vs ArrayScan (Single Term)", fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axhline(y=1, color='r', linestyle='--', alpha=0.5, label='Baseline')
        plt.tight_layout()
        plt.savefig(output_dir / "speedup_comparison.png", dpi=300)
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
    
    print(f"Loaded {total_docs} documents from {DATA_CSV}")
    print(f"Benchmarking {len(limits)} corpus sizes: {limits}")
    print(f"Discovered {len(ordered_names)} index implementations: {', '.join(ordered_names)}")

    rows: List[Dict] = []
    
    for limit in limits:
        subset = records[:limit]
        print(f"\n{'='*60}")
        print(f"Corpus Size: {limit:,} documents")
        print(f"{'='*60}")
        
        for index_name in ordered_names:
            factory = index_factories[index_name]
            engine, build_time, peak_mem, actual_mem, stats = build_engine(factory, subset)
            query_timings = measure_queries(engine)
            
            row = {
                "corpus_size": limit,
                "index_name": index_name,
                "build_time_s": build_time,
                "peak_memory_mib": peak_mem,
                "index_memory_mib": actual_mem,
                "vocabulary_size": stats['vocabulary_size'],
                "total_postings": stats['total_postings'],
                "avg_posting_length": stats['avg_posting_length'],
            }
            
            for label in [q[0] for q in QUERIES]:
                row[f"{label}_time_ms"] = query_timings[label][0]
                row[f"{label}_results"] = query_timings[label][1]
            
            rows.append(row)
            
            print(f"\n{index_name}:")
            print(f"  Build Time:      {build_time:.4f}s")
            print(f"  Peak Memory:     {peak_mem:.2f} MiB")
            print(f"  Index Memory:    {actual_mem:.2f} MiB")
            print(f"  Vocabulary:      {stats['vocabulary_size']:,} unique terms")
            print(f"  Total Postings:  {stats['total_postings']:,}")
            if stats['avg_posting_length'] > 0:
                print(f"  Avg Post. Len:   {stats['avg_posting_length']:.1f}")
            
            print(f"  Query Times:")
            for label in [q[0] for q in QUERIES]:
                time_ms = query_timings[label][0]
                count = query_timings[label][1]
                print(f"    {label:12s}: {time_ms:8.4f}ms ({count:,} results)")

    # Calculate and print growth rates
    print(f"\n{'='*60}")
    print("GROWTH RATE ANALYSIS")
    print(f"{'='*60}")
    
    for index_name in ordered_names:
        build_times = [row["build_time_s"] for row in rows if row["index_name"] == index_name]
        query_times = [row["single_time_ms"] for row in rows if row["index_name"] == index_name]
        
        build_growth = calculate_growth_rate(limits, build_times)
        query_growth = calculate_growth_rate(limits, [t for t in query_times if t > 0])
        
        print(f"\n{index_name}:")
        print(f"  Build time growth: O(n^{build_growth:.3f})")
        print(f"  Query time growth: O(n^{query_growth:.3f})")

    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "enhanced_benchmark_summary.csv"
    write_csv(csv_path, rows)
    print(f"\nResults saved to {csv_path}")
    
    # Generate plots
    plot_results(output_dir, rows, ordered_names)
    print(f"Plots saved in {output_dir}")
    print(f"\n{'='*60}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main(sys.argv[1:])
