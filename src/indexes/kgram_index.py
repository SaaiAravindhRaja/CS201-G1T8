"""Character k-gram inverted index for substring matching over raw text."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Mapping, Sequence, Set, List

from .base import Matcher
from ..text_utils import find_substring_positions


class KGram(Matcher):
    """
    Character k-gram inverted index for substring matching.
    """

    def __init__(self, k: int = 3) -> None:
        """
        Initialize k-gram index.

        Args:
            k: Length of character substrings to index (default 3).
               Smaller k -> more grams -> more matches but slower.
               Larger k -> fewer grams -> faster but fewer matches.
        """
        self.k = k
        self._postings: Dict[str, Set[str]] = defaultdict(set)
        self._doc_texts: Dict[str, str] = {}

    def build(self, documents: Mapping[str, str]) -> None:
        """Build k-gram postings directly from raw, lowercased document text."""
        self._postings = defaultdict(set)
        self._doc_texts = {}

        for doc_id, text in documents.items():
            text_lower = text.lower()
            self._doc_texts[doc_id] = text_lower
            if len(text_lower) < self.k:
                continue
            for i in range(len(text_lower) - self.k + 1):
                gram = text_lower[i : i + self.k]
                self._postings[gram].add(doc_id)

    def lookup_term(self, term: str, doc_id: str) -> List[int]:
        """
        Algorithm:
        1. Generate k-grams of the query term
        2. For each gram, get candidate doc_ids from postings
        3. Intersect the candidate sets (docs must have ALL grams)
        4. Verify candidates: confirm term appears as substring in doc tokens
        5. Return verified doc_ids
        """
        term_lower = term.lower()

        # Special case: term shorter than k -> fallback to scan in this doc
        if len(term_lower) < self.k:
            text = self._doc_texts.get(doc_id, "")
            return find_substring_positions(text, term_lower)

        # Generate k-grams of query term
        query_grams = [
            term_lower[i : i + self.k] for i in range(len(term_lower) - self.k + 1)
        ]

        # Intersect postings of all query grams to decide if this doc is candidate
        candidates = None
        for gram in query_grams:
            if gram not in self._postings:
                return []  # Fast negative: gram not indexed
            if candidates is None:
                candidates = set(self._postings[gram])
            else:
                candidates &= self._postings[gram]
            if not candidates:
                return []  # Early termination

        # If the requested doc is not in candidates, no matches
        if doc_id not in candidates:
            return []
        # Verify and collect all positions in the requested doc
        text = self._doc_texts.get(doc_id, "")
        return find_substring_positions(text, term_lower)

    def get_statistics(self) -> dict:
        """Return statistics about the k-gram index."""
        vocab_size = len(self._postings)
        total_postings = sum(len(posting_set) for posting_set in self._postings.values())
        avg_posting_length = (
            total_postings / vocab_size if vocab_size > 0 else 0
        )
        return {
            "k": self.k,
            "vocabulary_size": vocab_size,
            "avg_posting_length": avg_posting_length,
            "num_documents": len(self._doc_texts),
        }


__all__ = ["KGram"]
