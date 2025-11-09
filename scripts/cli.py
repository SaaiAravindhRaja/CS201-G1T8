#!/usr/bin/env python3
"""Minimal CLI for searching all reviews in a dataset (multi-pattern AND/OR)."""

from __future__ import annotations

import shlex
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.indexes import KMP, KGram, SuffixArray, SuffixArrayLogSq, AhoCorasick
from src.corpus import iter_reviews_from_csv

DATASETS: Dict[str, Path] = {
    "airline": Path("data/raw/airline.csv"),
    "airport": Path("data/raw/airport.csv"),
    "lounge": Path("data/raw/lounge.csv"),
    "seat": Path("data/raw/seat.csv"),
}

HELP = ("Commands:\n"
        "  backend <kmp|ac|sa|salog2|kgram> <dataset> [limit]\n"
        "      Build backend over dataset (default limit: 50000).\n"
        "      dataset ∈ {airline, airport, lounge, seat}\n"
        "  query --patterns \"a,b,c\" --mode <and|or> [--show-text]\n"
        "      Search ALL loaded reviews; prints matching doc_ids (and text if requested)\n"
        "  help | exit | quit\n")


class State:
    def __init__(self) -> None:
        self.records: List[tuple[str, str]] = []
        self.backend: str | None = None
        self.index_obj: object | None = None
        self.ac: AhoCorasick | None = None
        self.last_build_s: float = 0.0
        self.dataset: str = ""


def load_records(limit: int, dataset: str) -> List[tuple[str, str]]:
    dataset = dataset.lower()
    if dataset not in DATASETS:
        raise ValueError("dataset must be one of airline, airport, lounge, seat")
    csv_path = DATASETS[dataset]
    source_tag = dataset
    out: List[tuple[str, str]] = []
    for doc_id, text in iter_reviews_from_csv(csv_path, source_tag):
        out.append((doc_id, text))
        if len(out) >= limit:
            break
    if not out:
        raise ValueError("dataset appears empty")
    return out


def run_index_query(index_obj, records: Sequence[tuple[str, str]], patterns: Sequence[str], mode: str) -> tuple[float, List[str]]:
    match_all = mode == "and"
    matched: List[str] = []
    t0 = time.perf_counter()
    for doc_id, _ in records:
        hits = [bool(index_obj.lookup_term(pattern, doc_id)) for pattern in patterns]
        if match_all and all(hits):
            matched.append(doc_id)
        elif not match_all and any(hits):
            matched.append(doc_id)
    elapsed = (time.perf_counter() - t0) * 1000.0
    return elapsed, matched


def run_ac_query(ac: AhoCorasick, records: Sequence[tuple[str, str]], patterns: Sequence[str], mode: str) -> tuple[float, List[str]]:
    ac.build_patterns(patterns)
    matched: List[str] = []
    t0 = time.perf_counter()
    for doc_id, _text in records:
        pairs = ac.match(doc_id)
        found = {pat for pat, _ in pairs}
        ok = all(p in found for p in patterns) if mode == "and" else bool(found)
        if ok:
            matched.append(doc_id)
    elapsed = (time.perf_counter() - t0) * 1000.0
    return elapsed, matched


def parse_patterns(args: List[str]) -> tuple[List[str], str, bool]:
    try:
        idx = args.index("--patterns")
    except ValueError:
        raise ValueError("Usage: query --patterns \"a,b,c\" --mode <and|or>")
    if idx + 1 >= len(args):
        raise ValueError("Usage: query --patterns \"a,b,c\" --mode <and|or>")
    raw = args[idx + 1]
    pats = [p.strip() for p in raw.split(',') if p.strip()]
    if not pats:
        raise ValueError("No patterns provided.")
    mode = "or"
    if "--mode" in args:
        try:
            mode = args[args.index("--mode") + 1]
        except Exception:
            raise ValueError("--mode requires 'and' or 'or'")
    if mode not in ("and", "or"):
        raise ValueError("--mode must be 'and' or 'or'")
    show_text = "--show-text" in args
    return pats, mode, show_text


def handle_backend(st: State, args: List[str]) -> None:
    if len(args) < 2 or args[0] not in ("kmp", "ac", "sa", "salog2", "kgram"):
        print("Usage: backend <kmp|ac|sa|salog2|kgram> <dataset> [limit]")
        return
    backend = args[0]
    dataset = args[1]
    limit = 50000
    if len(args) >= 3:
        try:
            limit = int(args[2])
        except ValueError:
            print("limit must be an integer")
            return
    try:
        records = load_records(limit, dataset)
    except ValueError as exc:
        print(exc)
        return

    st.records = records
    st.dataset = dataset
    st.backend = backend
    st.index_obj = None
    st.ac = None

    t0 = time.perf_counter()
    if backend == "ac":
        st.ac = AhoCorasick()
        st.ac.build({doc: txt for doc, txt in records})
    else:
        matcher = {
            "kmp": KMP,
            "kgram": KGram,
            "sa": SuffixArray,
            "salog2": SuffixArrayLogSq,
        }[backend]()
        matcher.build(dict(records))
        st.index_obj = matcher
    st.last_build_s = time.perf_counter() - t0
    print(f"Backend ready: {backend} | dataset={dataset} | docs={len(records)} | build={st.last_build_s:.3f}s")
    print("Next: query --patterns \"a,b,c\" --mode <and|or> [--show-text]")


def handle_query(st: State, args: List[str]) -> None:
    if not st.records or st.backend is None:
        print("Run: backend <...> <dataset> [limit] first.")
        return
    try:
        patterns, mode, show_text = parse_patterns(args)
    except ValueError as exc:
        print(exc)
        return

    if st.backend == "ac":
        if st.ac is None:
            print("Backend not built. Run backend command again.")
            return
        ms, docs = run_ac_query(st.ac, st.records, patterns, mode)
    else:
        if st.index_obj is None:
            print("Backend not built. Run backend command again.")
            return
        ms, docs = run_index_query(st.index_obj, st.records, patterns, mode)

    print(f"{st.backend.upper():6s} build {st.last_build_s:.3f}s | query {ms:.3f}ms | matched {len(docs)} docs")
    if show_text:
        lookup = dict(st.records)
        for d in docs:
            text = lookup.get(d, "<missing>").replace("\n", " ")
            print(f"{d}: {text}")
    else:
        for d in docs:
            print(d)
    print("You can run another query or type 'exit' to quit.")


def repl() -> None:
    st = State()
    print("Substring Search CLI (searches entire dataset). Type 'help' for commands.")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        parts = shlex.split(line)
        cmd, *args = parts
        cmd = cmd.lower()

        if cmd in ("exit", "quit"):
            break
        if cmd == "help":
            print(HELP)
        elif cmd == "backend":
            handle_backend(st, args)
        elif cmd == "query":
            handle_query(st, args)
        else:
            print("Unknown command. Type 'help'.")


def main() -> None:
    repl()


if __name__ == "__main__":
    main()
