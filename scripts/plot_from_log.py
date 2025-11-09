#!/usr/bin/env python3
"""Parse textual benchmark output and generate plots in an output directory.

Usage:
  python scripts/plot_from_log.py --input results.txt --output-dir benchmark_graphs

Input format expected (example):
  Limit 100 docs
    AhoCorasick  build 0.000s | peak 0.1 MiB | substr_short:0.061ms, substr_medium:0.039ms, prefix:0.053ms, or_substr:0.092ms
    KGram        build 0.034s | peak 2.8 MiB | substr_short:0.066ms, ...

Generates:
  - build_time.png
  - memory_peak.png
  - <label>_query.png for each query label seen (e.g., substr_short_query.png)
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import matplotlib.pyplot as plt
except Exception as exc:  # pragma: no cover
    plt = None


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plot graphs from textual benchmark output")
    p.add_argument("--input", type=Path, required=True, help="Path to text file with benchmark output")
    p.add_argument("--output-dir", type=Path, default=Path("benchmark_graphs"))
    return p.parse_args(argv)


def parse_log(text: str) -> Tuple[List[int], List[Dict[str, float]], List[str]]:
    limits: List[int] = []
    rows: List[Dict[str, float]] = []
    indexes_seen: List[str] = []

    current_limit: int | None = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("Limit ") and line.endswith("docs"):
            # e.g., "Limit 100 docs"
            try:
                parts = line.split()
                current_limit = int(parts[1])
                limits.append(current_limit)
            except Exception:
                current_limit = None
            continue

        # Parse index lines only when within a Limit section
        if current_limit is None:
            continue

        if " build " not in line:
            continue

        # Name before the word 'build'
        name = line.split(" build ", 1)[0].strip()
        # extract build time
        m_build = re.search(r"build\s+([0-9]*\.?[0-9]+)s", line)
        # peak memory
        m_peak = re.search(r"peak\s+([0-9]*\.?[0-9]+)\s*MiB", line)
        # query timings (after last '|')
        timings_part = line.rsplit("|", 1)[-1]
        # Looks like: " substr_short:0.061ms, substr_medium:0.039ms, ..."
        label_ms: Dict[str, float] = {}
        for chunk in timings_part.split(','):
            chunk = chunk.strip()
            if not chunk:
                continue
            if ':' not in chunk:
                continue
            label, val = [s.strip() for s in chunk.split(':', 1)]
            if val.endswith('ms'):
                try:
                    label_ms[label] = float(val[:-2])
                except Exception:
                    pass

        row: Dict[str, float] = {"limit": float(current_limit), "index": name}
        if m_build:
            try:
                row["build_time_s"] = float(m_build.group(1))
            except Exception:
                row["build_time_s"] = 0.0
        else:
            row["build_time_s"] = 0.0
        if m_peak:
            try:
                row["peak_memory_mib"] = float(m_peak.group(1))
            except Exception:
                row["peak_memory_mib"] = 0.0
        else:
            row["peak_memory_mib"] = 0.0

        for k, v in label_ms.items():
            row[f"{k}_ms"] = v

        rows.append(row)
        if name not in indexes_seen:
            indexes_seen.append(name)

    return limits, rows, indexes_seen


def plot(limits: List[int], rows: List[Dict[str, float]], index_names: List[str], outdir: Path) -> None:
    if plt is None:
        print("matplotlib not available; cannot plot")
        return
    outdir.mkdir(parents=True, exist_ok=True)

    limits_sorted = sorted(set(limits))

    # Build time
    plt.figure(figsize=(8, 5))
    for idx in index_names:
        ys = [r["build_time_s"] for r in rows if r["index"] == idx]
        xs = [int(r["limit"]) for r in rows if r["index"] == idx]
        xs, ys = zip(*sorted(zip(xs, ys))) if xs else ([], [])
        plt.plot(xs, ys, marker='o', label=idx)
    plt.xlabel("Documents indexed")
    plt.ylabel("Build time (s)")
    plt.title("Index Build Time vs Corpus Size")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "build_time.png", dpi=300)
    plt.close()

    # Special: compare SuffixArray vs SuffixArrayLogSq build times explicitly
    if {"SuffixArray", "SuffixArrayLogSq"}.issubset(set(index_names)):
        plt.figure(figsize=(8, 5))
        for idx in ["SuffixArray", "SuffixArrayLogSq"]:
            ys = [r["build_time_s"] for r in rows if r["index"] == idx]
            xs = [int(r["limit"]) for r in rows if r["index"] == idx]
            xs, ys = zip(*sorted(zip(xs, ys))) if xs else ([], [])
            plt.plot(xs, ys, marker='o', label=idx)
        plt.xlabel("Documents indexed")
        plt.ylabel("Build time (s)")
        plt.title("Suffix Array: Build Time (Radix vs Log^2)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(outdir / "build_time_suffix_array_variants.png", dpi=300)
        plt.close()

    # Peak memory
    plt.figure(figsize=(8, 5))
    for idx in index_names:
        ys = [r["peak_memory_mib"] for r in rows if r["index"] == idx]
        xs = [int(r["limit"]) for r in rows if r["index"] == idx]
        xs, ys = zip(*sorted(zip(xs, ys))) if xs else ([], [])
        plt.plot(xs, ys, marker='o', label=idx)
    plt.xlabel("Documents indexed")
    plt.ylabel("Peak memory (MiB)")
    plt.title("Peak Memory vs Corpus Size")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "memory_peak.png", dpi=300)
    plt.close()

    # Query timings: detect labels by columns ending with _ms
    all_keys = set().union(*(r.keys() for r in rows))
    labels = [k[:-3] for k in all_keys if k.endswith("_ms")]
    labels = sorted(labels)

    for label in labels:
        col = f"{label}_ms"
        plt.figure(figsize=(8, 5))
        for idx in index_names:
            xs = [int(r["limit"]) for r in rows if r["index"] == idx and col in r]
            ys = [r[col] for r in rows if r["index"] == idx and col in r]
            if not xs:
                continue
            xs, ys = zip(*sorted(zip(xs, ys)))
            plt.plot(xs, ys, marker='o', label=idx)
        plt.xlabel("Documents indexed")
        plt.ylabel("Query time (ms)")
        plt.title(f"Query '{label}' Performance")
        plt.legend()
        plt.tight_layout()
        plt.savefig(outdir / f"{label}_query.png", dpi=300)
        plt.close()


def main(argv: List[str]) -> None:
    args = parse_args(argv)
    text = args.input.read_text(encoding="utf-8", errors="ignore")
    limits, rows, idxs = parse_log(text)
    if not rows:
        print("No data parsed from log; aborting")
        return
    plot(limits, rows, idxs, args.output_dir)
    print(f"Saved plots in {args.output_dir}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
