#!/usr/bin/env python3
"""Interactive CLI for Skytrax Reviews Search Engine."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src import (
    ArrayScanIndex,
    InvertedIndex,
    BloomFilterIndex,
    KGramIndex,
    SuffixArrayIndex,
    SearchEngine,
)
from src.corpus import iter_reviews_from_csv

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Available index implementations
INDEX_TYPES = {
    "1": ("Array Scan", ArrayScanIndex),
    "2": ("Inverted Index", InvertedIndex),
    "3": ("Bloom Filter", BloomFilterIndex),
    "4": ("K-Gram Index", KGramIndex),
    "5": ("Suffix Array", SuffixArrayIndex),
}

# Available datasets
DATASETS = {
    "1": ("Airlines", Path("data/raw/airline.csv"), "airline"),
    "2": ("Airports", Path("data/raw/airport.csv"), "airport"),
    "3": ("Seats", Path("data/raw/seat.csv"), "seat"),
    "4": ("Lounges", Path("data/raw/lounge.csv"), "lounge"),
}


def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}\n")


def print_section(text: str) -> None:
    """Print a section divider."""
    print(f"\n{Colors.YELLOW}{'-' * 70}{Colors.END}")
    print(f"{Colors.YELLOW}{text}{Colors.END}")
    print(f"{Colors.YELLOW}{'-' * 70}{Colors.END}")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}[OK]{Colors.END} {text}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}[i]{Colors.END} {text}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}[X]{Colors.END} {text}")


def get_input(prompt: str) -> str:
    """Get user input with styled prompt."""
    return input(f"{Colors.BOLD}{prompt}{Colors.END} ").strip()


def select_dataset() -> tuple[str, Path, str] | None:
    """Let user select a dataset. Returns None if user wants to go back."""
    print_section("SELECT DATASET")
    for key, (name, path, _) in DATASETS.items():
        exists = "[OK]" if path.exists() else "[X]"
        print(f"  {Colors.BOLD}{key}.{Colors.END} {name} {exists}")

    print(f"\n  {Colors.BOLD}b.{Colors.END} Back to Main Menu")
    print(f"  {Colors.BOLD}q.{Colors.END} Exit")

    while True:
        choice = get_input("\nChoose dataset [default: 1 - Airlines]:").lower().strip()

        # Default to Airlines
        if not choice:
            choice = "1"

        # Handle back/exit
        if choice in ["b", "back"]:
            return None
        if choice in ["q", "quit", "exit"]:
            print_header("Thank you for using Skytrax Search Engine!")
            sys.exit(0)

        # Handle dataset selection
        if choice in DATASETS:
            name, path, tag = DATASETS[choice]
            if not path.exists():
                print_error(f"Dataset not found at {path}")
                continue
            print_success(f"Selected: {name}")
            return name, path, tag

        print_error("Invalid choice. Enter 1-4, 'b' (back), or 'q' (quit).")


def load_documents(engine: SearchEngine, csv_path: Path, source_tag: str, limit: int) -> tuple[int, float]:
    """Load documents into the search engine."""
    records = []
    for doc_id, text in iter_reviews_from_csv(csv_path, source_tag=source_tag):
        records.append((doc_id, text))
        if len(records) >= limit:
            break

    if not records:
        return 0, 0.0

    start_time = time.perf_counter()
    for doc_id, text in records:
        engine.add_document(doc_id, text)
    build_time = time.perf_counter() - start_time

    return len(records), build_time


def compare_indexes(csv_path: Path, source_tag: str, query: str, match_mode: str = "and", limit: int = 1000) -> None:
    """Compare performance across all index types."""
    print_section(f"RUNNING QUERY: '{query}' (Mode: {match_mode.upper()})")
    print_info(f"Dataset: {csv_path.name} | Documents: {limit:,}")

    results = []

    for key, (name, index_class) in INDEX_TYPES.items():
        print(f"\n{Colors.CYAN}Testing {name}...{Colors.END}", end=" ", flush=True)

        try:
            engine = SearchEngine(index_class())

            # Load documents
            doc_count, build_time = load_documents(engine, csv_path, source_tag, limit)

            if doc_count == 0:
                print(f"{Colors.RED}[FAILED]{Colors.END}")
                continue

            # Run query
            start_time = time.perf_counter()
            matches = engine.search(query, match_mode=match_mode)
            query_time = time.perf_counter() - start_time

            results.append({
                "name": name,
                "build_time": build_time,
                "query_time": query_time,
                "matches": len(matches),
                "docs": doc_count,
            })

            print(f"{Colors.GREEN}[DONE]{Colors.END}")

        except Exception as e:
            print(f"{Colors.RED}[ERROR: {e}]{Colors.END}")
            continue

    # Display results table
    if results:
        print_section("COMPARISON RESULTS")
        print(f"\n{Colors.BOLD}{'Index Type':<20} {'Build Time':<15} {'Query Time':<15} {'Matches':<10}{Colors.END}")
        print("=" * 70)

        for r in results:
            print(f"{r['name']:<20} {r['build_time']:>10.3f}s     {r['query_time']*1000:>10.2f}ms     {r['matches']:>8,}")

        # Find fastest
        fastest_build = min(results, key=lambda x: x['build_time'])
        fastest_query = min(results, key=lambda x: x['query_time'])

        print("=" * 70)
        print(f"\n{Colors.BOLD}Performance Summary:{Colors.END}")
        print(f"  {Colors.GREEN}Fastest Build:{Colors.END} {fastest_build['name']} ({fastest_build['build_time']:.3f}s)")
        print(f"  {Colors.GREEN}Fastest Query:{Colors.END} {fastest_query['name']} ({fastest_query['query_time']*1000:.2f}ms)")
        print(f"  {Colors.BLUE}Total Documents:{Colors.END} {results[0]['docs']:,}")
        print(f"  {Colors.BLUE}Total Matches:{Colors.END} {results[0]['matches']:,}")
    else:
        print_error("No results to display")


def get_query_input() -> str | None:
    """Get query from user. Returns None if user wants to go back."""
    print(f"\n{Colors.BOLD}Enter your search query{Colors.END}")
    print(f"  {Colors.BOLD}b.{Colors.END} Back to Dataset Selection")
    print(f"  {Colors.BOLD}q.{Colors.END} Exit")

    query = get_input("\nQuery:").strip()

    if query.lower() in ["b", "back"]:
        return None
    if query.lower() in ["q", "quit", "exit"]:
        print_header("Thank you for using Skytrax Search Engine!")
        sys.exit(0)

    if not query:
        print_error("Query cannot be empty")
        return get_query_input()  # Recursive retry

    return query


def get_match_mode() -> str | None:
    """Get match mode from user. Returns None if user wants to go back."""
    print(f"\n{Colors.BOLD}Match Mode{Colors.END}")
    print("  AND - All terms must be present (stricter)")
    print("  OR  - Any term can be present (broader)")
    print(f"\n  {Colors.BOLD}b.{Colors.END} Back to Query")
    print(f"  {Colors.BOLD}q.{Colors.END} Exit")

    mode_input = get_input("\nMatch mode [default: AND]:").lower().strip()

    if not mode_input:
        return "and"

    if mode_input in ["b", "back"]:
        return None
    if mode_input in ["q", "quit", "exit"]:
        print_header("Thank you for using Skytrax Search Engine!")
        sys.exit(0)

    if mode_input in ["and", "or"]:
        return mode_input

    print_error("Invalid choice. Enter 'and', 'or', 'b' (back), or 'q' (quit).")
    return get_match_mode()  # Recursive retry


def get_document_limit() -> int | None:
    """Get document limit from user. Returns None if user wants to go back."""
    print(f"\n{Colors.BOLD}Document Limit{Colors.END}")
    print(f"  {Colors.BOLD}b.{Colors.END} Back to Match Mode")
    print(f"  {Colors.BOLD}q.{Colors.END} Exit")

    limit_str = get_input("\nNumber of documents to load [default: 1000]:").strip()

    if not limit_str:
        return 1000

    if limit_str.lower() in ["b", "back"]:
        return None
    if limit_str.lower() in ["q", "quit", "exit"]:
        print_header("Thank you for using Skytrax Search Engine!")
        sys.exit(0)

    if limit_str.isdigit() and int(limit_str) > 0:
        return int(limit_str)

    print_error("Invalid input. Enter a positive number, 'b' (back), or 'q' (quit).")
    return get_document_limit()  # Recursive retry


def main_menu() -> None:
    """Main interactive menu."""
    while True:
        print_header("SKYTRAX REVIEWS SEARCH ENGINE")
        print(f"{Colors.BOLD}Compare all 5 index implementations with your query{Colors.END}\n")

        print("{0}OPTIONS:{1}".format(Colors.BOLD, Colors.END))
        print("  1. Run Query (Compare All Indexes)")
        print("  2. Exit")

        choice = get_input("\nSelect option (1-2):").strip()

        if choice == "1":
            # Navigation flow with back support using state machine
            state = "dataset"
            csv_path = None
            source_tag = None
            query = None
            mode = None

            while state != "done":
                if state == "dataset":
                    result = select_dataset()
                    if result is None:
                        break  # Back to main menu
                    _, csv_path, source_tag = result
                    state = "query"

                elif state == "query":
                    query = get_query_input()
                    if query is None:
                        state = "dataset"  # Back to dataset
                    else:
                        state = "mode"

                elif state == "mode":
                    mode = get_match_mode()
                    if mode is None:
                        state = "query"  # Back to query
                    else:
                        state = "limit"

                elif state == "limit":
                    limit = get_document_limit()
                    if limit is None:
                        state = "mode"  # Back to match mode
                    else:
                        # Run comparison
                        print("")  # Add spacing
                        compare_indexes(csv_path, source_tag, query, mode, limit)

                        # Ask if user wants to continue
                        print("")
                        input(f"{Colors.BOLD}Press Enter to continue...{Colors.END}")
                        state = "done"

        elif choice == "2" or choice.lower() in ["q", "quit", "exit"]:
            print_header("Thank you for using Skytrax Search Engine!")
            break

        else:
            print_error("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user. Goodbye!{Colors.END}")
        sys.exit(0)
