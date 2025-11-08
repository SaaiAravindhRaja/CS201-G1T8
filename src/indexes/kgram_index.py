"""Character k-gram inverted index for substring matching."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Sequence, Set

from .base import Index


class KGramIndex(Index):
    """Character k-gram inverted index for substring/fuzzy matching.

    Instead of indexing by exact tokens, this index generates all k-length
    character substrings (k-grams) of each token and maintains postings for
    each gram. Lookup requires verification to ensure the query substring
    actually appears in the candidate documents.

    Trade-offs:
    - Memory: higher than exact inverted (more postings due to grams)
    - Build time: higher (generating all grams per token)
    - Query time: depends on gram selectivity and verification cost
    - Results: distinct from exact matching (substring matches)
    """

    def __init__(self, k: int = 3) -> None:
        """Initialize k-gram index.

        Args:
            k: Length of character substrings to index (default 3).
               Smaller k -> more grams -> more matches but slower.
               Larger k -> fewer grams -> faster but fewer matches.
        """
        self.k = k
        # gram -> set of doc_ids
        self._postings: Dict[str, Set[str]] = defaultdict(set)
        # doc_id -> set of original tokens (for verification)
        self._documents: Dict[str, Set[str]] = {}

    def add_document(self, doc_id: str, tokens: Sequence[str]) -> None:
        """Add document by indexing character k-grams of each token.

        Time: O(sum of (len(token) - k + 1) for each token)
        """
        # store lowercase tokens for consistent matching & cheaper verification
        token_set = {t.lower() for t in tokens}
        self._documents[doc_id] = token_set

        for token_lower in token_set:
            # For short tokens, index the whole token as a single gram
            if len(token_lower) < self.k:
                self._postings[token_lower].add(doc_id)
            else:
                # Generate all k-grams of this token
                for i in range(len(token_lower) - self.k + 1):
                    gram = token_lower[i : i + self.k]
                    self._postings[gram].add(doc_id)

    def lookup_term(self, term: str) -> Set[str]:
        """Lookup documents containing the term as a substring.

        Algorithm:
        1. Generate k-grams of the query term
        2. For each gram, get candidate doc_ids from postings
        3. Intersect the candidate sets (docs must have ALL grams)
        4. Verify candidates: confirm term appears as substring in doc tokens
        5. Return verified doc_ids

        This two-phase approach (candidate generation + verification) avoids
        false positives from gram collisions.
        """
        term_lower = term.lower()

        # Special case: term shorter than k
        if len(term_lower) < self.k:
            # Treat entire term as a gram
            return self._postings.get(term_lower, set()).copy()

        # Generate k-grams of query term
        query_grams = [
            term_lower[i : i + self.k] for i in range(len(term_lower) - self.k + 1)
        ]

        # Intersect postings of all query grams
        candidates = None
        for gram in query_grams:
            if gram not in self._postings:
                return set()  # Fast negative: gram not indexed
            if candidates is None:
                candidates = set(self._postings[gram])
            else:
                candidates &= self._postings[gram]
            if not candidates:
                return set()  # Early termination

        # Phase 2: Verify candidates
        # A candidate doc may have all grams but the term substring may not appear
        # (gram collision). Verify by checking if term appears in any token.
        results = set()
        for doc_id in candidates:
            # tokens are stored lowercased already
            for token in self._documents[doc_id]:
                if term_lower in token:
                    results.add(doc_id)
                    break
        return results

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
            "num_documents": len(self._documents),
        }


__all__ = ["KGramIndex"]
