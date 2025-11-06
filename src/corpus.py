"""Utilities to ingest review corpora into the shared search engine."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator, Tuple


def iter_reviews_from_csv(
    csv_path: Path,
    source_tag: str,
    text_field: str = "content",
    encoding: str = "utf-8",
) -> Iterator[Tuple[str, str]]:
    """Yield (doc_id, text) tuples from a CSV file."""
    with csv_path.open("r", newline="", encoding=encoding) as handle:
        reader = csv.DictReader(handle)
        for row_index, row in enumerate(reader):
            text = row.get(text_field, "") or ""
            if not text.strip():
                continue
            doc_id = f"{source_tag}:{row_index}"
            yield (doc_id, text)
