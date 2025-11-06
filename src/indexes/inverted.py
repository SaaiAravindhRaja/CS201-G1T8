"""Inverted index storing document postings per term."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Sequence, Set

from .base import Index


class InvertedIndex(Index):
    """Hash-map based inverted index for exact term matching."""

    def __init__(self) -> None:
        self._postings: Dict[str, Set[str]] = defaultdict(set)

    def add_document(
        self,
        doc_id: str,
        tokens: Sequence[str],
    ) -> None:
        for token in set(tokens):
            self._postings[token].add(doc_id)

    def lookup_term(self, term: str) -> Set[str]:
        return self._postings.get(term, set())


__all__ = ["InvertedIndex"]
