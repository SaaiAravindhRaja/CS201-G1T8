#!/usr/bin/env python3
"""Run a quick keyword query against the review corpus."""

from __future__ import annotations

import argparse
import sys
import textwrap
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src import InvertedIndex, SearchEngine
from src.corpus import iter_reviews_from_csv

DATA_CSV = Path("data/raw/airline.csv")
SOURCE_TAG = "airline"


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Execute a keyword query (tokens separated by spaces).")
    parser.add_argument("query", help="Query string.")
    parser.add_argument(
        "--or",
        dest="use_or",
        action="store_true",
        help="Use OR semantics instead of AND.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of results to display (default: 5).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5000,
        help="Number of documents to load (default: 5000).",
    )
    return parser.parse_args(list(argv))


def main(argv) -> None:
    args = parse_args(argv)
    match_mode = "or" if args.use_or else "and"

    records = []
    for doc_id, text in iter_reviews_from_csv(DATA_CSV, source_tag=SOURCE_TAG):
        records.append((doc_id, text))
        if len(records) >= args.limit:
            break

    if not records:
        print("No documents loaded from dataset.", file=sys.stderr)
        raise SystemExit(1)

    engine = SearchEngine(InvertedIndex())
    start = time.perf_counter()
    for doc_id, text in records:
        engine.add_document(doc_id, text)
    build_time = time.perf_counter() - start

    query_start = time.perf_counter()
    matches = engine.search(args.query, match_mode=match_mode)
    query_time = time.perf_counter() - query_start

    print(f"Loaded {len(records)} documents in {build_time:.3f}s using inverted index.")
    print(f"Query '{args.query}' (mode={match_mode}) matched {len(matches)} docs in {query_time:.3f}s.")

    for doc in matches[: args.top]:
        snippet = textwrap.shorten(doc.text.replace("\n", " "), width=160, placeholder="…")
        print(f"- {doc.doc_id}: {snippet}")


if __name__ == "__main__":
    main(sys.argv[1:])
