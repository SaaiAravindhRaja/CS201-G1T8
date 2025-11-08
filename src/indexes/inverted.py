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
        # canonicalize tokens to lowercase to avoid case-sensitivity bugs
        for token in {t.lower() for t in tokens}:
            self._postings[token].add(doc_id)

    def lookup_term(self, term: str) -> Set[str]:
        return set(self._postings.get(term.lower(), set()))


__all__ = ["InvertedIndex"]
