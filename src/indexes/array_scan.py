"""Baseline array-scan index used for correctness benchmarking."""

from __future__ import annotations

from typing import Dict, List, Sequence, Set

from .base import Index


class ArrayScanIndex(Index):
    """Baseline ``O(n)`` scan over token lists for every query."""

    def __init__(self) -> None:
        self._documents: Dict[str, List[str]] = {}

    def add_document(
        self,
        doc_id: str,
        tokens: Sequence[str],
    ) -> None:
        self._documents[doc_id] = list(tokens)

    def lookup_term(self, term: str) -> Set[str]:
        matched: Set[str] = set()
        for doc_id, tokens in self._documents.items():
            if term in tokens:
                matched.add(doc_id)
        return matched


__all__ = ["ArrayScanIndex"]
