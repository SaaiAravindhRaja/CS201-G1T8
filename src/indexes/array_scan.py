"""Baseline array-scan index used for correctness benchmarking."""

from __future__ import annotations

from typing import Dict, List, Sequence, Set

from .base import Index


class ArrayScanIndex(Index):
    """Baseline ``O(n)`` scan over token lists for every query."""

    def __init__(self) -> None:
        # store tokens as a set of lowercased strings for faster membership checks
        self._documents: Dict[str, Set[str]] = {}

    def add_document(
        self,
        doc_id: str,
        tokens: Sequence[str],
    ) -> None:
        self._documents[doc_id] = {t.lower() for t in tokens}

    def lookup_term(self, term: str) -> Set[str]:
        term = term.lower()
        matched: Set[str] = set()
        for doc_id, tokens in self._documents.items():
            if term in tokens:
                matched.add(doc_id)
        return matched


__all__ = ["ArrayScanIndex"]
