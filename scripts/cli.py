#!/usr/bin/env python3
"""Interactive CLI for searching reviews using different substring matching algorithms."""

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

# Data structure explanations
ALGORITHMS = {
    "kmp": {
        "name": "KMP (Knuth-Morris-Pratt)",
        "desc": "Linear-time string matching using failure function",
        "complexity": "O(n+m) per query | O(n) space",
        "best_for": "Single pattern searches, guaranteed linear time"
    },
    "ac": {
        "name": "Aho-Corasick",
        "desc": "Trie-based multi-pattern matching with failure links",
        "complexity": "O(n+m+z) where z=matches | O(alphabet×states) space",
        "best_for": "Multiple patterns simultaneously (e.g., AND/OR queries)"
    },
    "kgram": {
        "name": "K-Gram Index",
        "desc": "Character-level inverted index (k=3 substrings)",
        "complexity": "O(k) lookup + O(candidates) verification | O(vocabulary×docs) space",
        "best_for": "Fuzzy/substring search with moderate corpus size"
    },
    "sa": {
        "name": "Suffix Array",
        "desc": "Sorted array of all text suffixes with binary search",
        "complexity": "O(m log n) query | O(n) build, O(n) space",
        "best_for": "Substring queries after one-time O(n log n) build"
    },
    "salog2": {
        "name": "Suffix Array + LCP",
        "desc": "Enhanced suffix array with Longest Common Prefix",
        "complexity": "O(m + log n) query | O(n) space with LCP array",
        "best_for": "Repeated substring queries with better constants"
    }
}

HELP = """
╔════════════════════════════════════════════════════════════════════════════╗
║                   SUBSTRING SEARCH CLI - COMMANDS                          ║
╚════════════════════════════════════════════════════════════════════════════╝

📚 ALGORITHMS:
  info                Show detailed comparison of all algorithms
  info <algorithm>    Show details about specific algorithm
                      (kmp, ac, kgram, sa, salog2)

🔧 SETUP:
  backend <algorithm> <dataset> [limit]
      Build index using specified algorithm (default limit: 50000)
      Datasets: airline, airport, lounge, seat
      
      Example: backend ac airline 1000

🔍 SEARCH:
  query --patterns "wifi,delay" --mode <and|or> [--show-text]
      Search loaded documents for patterns
      --mode and: Match documents containing ALL patterns
      --mode or:  Match documents containing ANY pattern
      --show-text: Display matching document text
      
      Example: query --patterns "wifi,free" --mode and --show-text

💡 OTHER:
  help     Show this help message
  exit     Quit the CLI
  quit     Quit the CLI

"""


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
        print("❌ Usage: backend <kmp|ac|sa|salog2|kgram> <dataset> [limit]")
        print("   Example: backend ac airline 1000")
        print("   Type 'info' to see algorithm comparison")
        return
    
    backend = args[0]
    dataset = args[1]
    limit = 50000
    
    if len(args) >= 3:
        try:
            limit = int(args[2])
        except ValueError:
            print("❌ limit must be an integer")
            return
    
    print(f"\n🔨 Building {ALGORITHMS[backend]['name']}...")
    print(f"📊 Dataset: {dataset} | Limit: {limit} documents")
    
    try:
        records = load_records(limit, dataset)
    except ValueError as exc:
        print(f"❌ {exc}")
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
    
    print(f"\n✅ Backend ready!")
    print(f"   Algorithm: {ALGORITHMS[backend]['name']}")
    print(f"   Dataset: {dataset}")
    print(f"   Documents: {len(records):,}")
    print(f"   Build time: {st.last_build_s:.3f}s")
    print(f"\n💡 Next: query --patterns \"wifi,delay\" --mode and\n")


def handle_query(st: State, args: List[str]) -> None:
    if not st.records or st.backend is None:
        print("❌ No backend loaded. Run: backend <algorithm> <dataset> [limit]")
        print("   Example: backend ac airline 1000")
        return
    
    try:
        patterns, mode, show_text = parse_patterns(args)
    except ValueError as exc:
        print(f"❌ {exc}")
        return

    print(f"\n🔍 Searching with {ALGORITHMS[st.backend]['name']}...")
    print(f"   Patterns: {patterns}")
    print(f"   Mode: {mode.upper()}")
    
    if st.backend == "ac":
        if st.ac is None:
            print("❌ Backend not built. Run backend command again.")
            return
        ms, docs = run_ac_query(st.ac, st.records, patterns, mode)
    else:
        if st.index_obj is None:
            print("❌ Backend not built. Run backend command again.")
            return
        ms, docs = run_index_query(st.index_obj, st.records, patterns, mode)

    print(f"\n📊 RESULTS:")
    print(f"   Algorithm: {st.backend.upper()}")
    print(f"   Build time: {st.last_build_s:.3f}s")
    print(f"   Query time: {ms:.3f}ms")
    print(f"   Matches: {len(docs):,} documents")
    
    if show_text:
        print(f"\n📄 MATCHED DOCUMENTS:\n")
        lookup = dict(st.records)
        for i, d in enumerate(docs[:10], 1):  # Show first 10
            text = lookup.get(d, "<missing>").replace("\n", " ")
            print(f"{i}. [{d}]")
            print(f"   {text[:150]}{'...' if len(text) > 150 else ''}\n")
        if len(docs) > 10:
            print(f"   ... and {len(docs) - 10} more documents")
    else:
        print(f"\n📋 DOCUMENT IDs (showing first 20):")
        for d in docs[:20]:
            print(f"   • {d}")
        if len(docs) > 20:
            print(f"   ... and {len(docs) - 20} more")
    
    print(f"\n💡 Run another query or type 'exit' to quit\n")


def show_algorithm_info(algorithm: str | None = None) -> None:
    """Display information about algorithms."""
    if algorithm is None:
        # Show comparison table
        print("\n" + "="*100)
        print("ALGORITHM COMPARISON".center(100))
        print("="*100 + "\n")
        
        for key, info in ALGORITHMS.items():
            print(f"🔹 {key.upper()} - {info['name']}")
            print(f"   Description: {info['desc']}")
            print(f"   Complexity:  {info['complexity']}")
            print(f"   Best for:    {info['best_for']}")
            print()
        
        print("="*100)
        print("Legend: n = text length, m = pattern length, k = k-gram size, z = output size")
        print("="*100)
        print("\n💡 Type 'info <algorithm>' for detailed explanation (e.g., 'info ac')\n")
        
    else:
        algo = algorithm.lower()
        if algo not in ALGORITHMS:
            print(f"Unknown algorithm: {algo}")
            print(f"Available: {', '.join(ALGORITHMS.keys())}")
            return
        
        info = ALGORITHMS[algo]
        print("\n" + "="*80)
        print(f"{info['name']}".center(80))
        print("="*80 + "\n")
        print(f"📝 Description: {info['desc']}")
        print(f"⚡ Complexity:   {info['complexity']}")
        print(f"✅ Best for:     {info['best_for']}")
        print("\n" + "="*80 + "\n")


def repl() -> None:
    st = State()
    print("\n" + "="*80)
    print("CS201 SUBSTRING SEARCH CLI".center(80))
    print("="*80)
    print("\n💡 Type 'help' for commands or 'info' for algorithm comparison\n")
    
    while True:
        try:
            if st.backend:
                prompt = f"[{st.backend.upper()} | {st.dataset} | {len(st.records)} docs]> "
            else:
                prompt = "> "
            line = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Goodbye!")
            break
        
        if not line:
            continue
        
        parts = shlex.split(line)
        cmd, *args = parts
        cmd = cmd.lower()

        if cmd in ("exit", "quit"):
            print("\n👋 Goodbye!")
            break
        elif cmd == "help":
            print(HELP)
        elif cmd == "info":
            show_algorithm_info(args[0] if args else None)
        elif cmd == "backend":
            handle_backend(st, args)
        elif cmd == "query":
            handle_query(st, args)
        else:
            print(f"❌ Unknown command: '{cmd}'. Type 'help' for available commands.")


def main() -> None:
    repl()


if __name__ == "__main__":
    main()
