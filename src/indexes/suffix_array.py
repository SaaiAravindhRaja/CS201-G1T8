"""Suffix array index for efficient substring pattern matching."""

from __future__ import annotations

from typing import Dict, List, Sequence, Set, Tuple

from .base import Index


class SuffixArrayIndex(Index):
    """Suffix array index for substring/prefix matching.

    A suffix array is a sorted array of all suffixes of a text. Combined with
    binary search and LCP (Longest Common Prefix) arrays, it enables efficient
    substring pattern matching.

    Trade-offs:
    - Memory: O(n) where n is total character count across all tokens
    - Build time: O(n log n) for suffix array construction
    - Query time: O(m log n + k) where m is pattern length, k is result count
    - Results: supports substring and prefix matching

    This implementation stores a mapping from suffix positions to document IDs,
    enabling efficient document retrieval for matching patterns.
    """

    def __init__(self) -> None:
        """Initialize suffix array index."""
        # Map doc_id to set of tokens
        self._documents: Dict[str, Set[str]] = {}
        # Combined text from all tokens (with separators)
        self._text: str = ""
        # Suffix array: sorted indices of suffixes
        self._suffix_array: List[int] = []
        # Map position in text to (doc_id, token)
        self._position_map: List[Tuple[str, str]] = []
        # Separator character (unlikely to appear in normal text)
        self._separator = "\x00"
        # Flag to track if rebuild is needed
        self._needs_rebuild = False

    def add_document(self, doc_id: str, tokens: Sequence[str]) -> None:
        """Add document by storing its tokens.

        Note: The suffix array is rebuilt lazily on first lookup after additions.
        """
        token_set = set(tokens)
        self._documents[doc_id] = token_set
        self._needs_rebuild = True

    def _rebuild_suffix_array(self) -> None:
        """Rebuild the suffix array from all stored documents.

        This creates a combined text from all tokens, builds the suffix array,
        and maintains a mapping from text positions to document IDs.
        """
        if not self._documents:
            self._text = ""
            self._suffix_array = []
            self._position_map = []
            self._needs_rebuild = False
            return

        # Build combined text and position map
        text_parts: List[str] = []
        position_map: List[Tuple[str, str]] = []

        for doc_id, tokens in self._documents.items():
            for token in tokens:
                token_lower = token.lower()
                # Add each character of the token
                for char in token_lower:
                    text_parts.append(char)
                    position_map.append((doc_id, token))

                # Add separator
                text_parts.append(self._separator)
                position_map.append((doc_id, token))

        self._text = "".join(text_parts)
        self._position_map = position_map

        n = len(self._text)
        if n == 0:
            self._suffix_array = []
            self._needs_rebuild = False
            return

        # Build suffix array using prefix-doubling (O(n log n))
        sa = list(range(n))
        rank = [ord(c) for c in self._text]
        tmp = [0] * n
        k = 1

        while True:
            sa.sort(key=lambda i: (rank[i], rank[i + k] if i + k < n else -1))
            tmp[sa[0]] = 0
            for i in range(1, n):
                prev = (rank[sa[i - 1]], rank[sa[i - 1] + k] if sa[i - 1] + k < n else -1)
                curr = (rank[sa[i]], rank[sa[i] + k] if sa[i] + k < n else -1)
                tmp[sa[i]] = tmp[sa[i - 1]] + (curr != prev)
            rank = tmp.copy()
            if rank[sa[-1]] == n - 1:
                break
            k <<= 1

        self._suffix_array = sa
        self._needs_rebuild = False

    def lookup_term(self, term: str) -> Set[str]:
        """Lookup documents containing the term as a substring.

        Algorithm:
        1. Rebuild suffix array if needed
        2. Use binary search to find the range of suffixes starting with term
        3. Collect document IDs from matching suffix positions
        4. Verify that the term actually appears in the document tokens
        """
        if self._needs_rebuild:
            self._rebuild_suffix_array()

        if not self._suffix_array or not term:
            return set()

        term_lower = term.lower()

        # Binary search for the leftmost suffix that starts with term
        left = self._binary_search_left(term_lower)
        if left == len(self._suffix_array):
            return set()  # No matches found

        # Binary search for the rightmost suffix that starts with term
        right = self._binary_search_right(term_lower)

        # Collect document IDs from matching positions
        candidate_docs: Dict[str, Set[str]] = {}
        for i in range(left, right):
            suffix_pos = self._suffix_array[i]
            if suffix_pos < len(self._position_map):
                doc_id, token = self._position_map[suffix_pos]
                candidate_docs.setdefault(doc_id, set()).add(token)

        # Verify that term actually appears in the tokens
        results: Set[str] = set()
        for doc_id, tokens in candidate_docs.items():
            for token in tokens:
                if term_lower in token.lower():
                    results.add(doc_id)
                    break

        return results

    def _binary_search_left(self, pattern: str) -> int:
        """Find leftmost suffix that starts with pattern.

        Returns the index in suffix_array, or len(suffix_array) if not found.
        """
        left, right = 0, len(self._suffix_array)

        while left < right:
            mid = (left + right) // 2
            suffix_pos = self._suffix_array[mid]
            suffix = self._text[suffix_pos:]

            if suffix < pattern:
                left = mid + 1
            else:
                right = mid

        # Verify that we found a match
        if left < len(self._suffix_array):
            suffix_pos = self._suffix_array[left]
            suffix = self._text[suffix_pos:]
            if suffix.startswith(pattern):
                return left

        return len(self._suffix_array)

    def _binary_search_right(self, pattern: str) -> int:
        """Find rightmost suffix that starts with pattern.

        Returns one past the last matching index in suffix_array.
        """
        left, right = 0, len(self._suffix_array)

        # Create a pattern that is just beyond our search pattern
        # by appending the maximum unicode character
        pattern_upper = pattern + "\uffff"

        while left < right:
            mid = (left + right) // 2
            suffix_pos = self._suffix_array[mid]
            suffix = self._text[suffix_pos:]

            if suffix < pattern_upper:
                left = mid + 1
            else:
                right = mid

        return left

    def get_statistics(self) -> dict:
        """Return statistics about the suffix array index."""
        if self._needs_rebuild:
            self._rebuild_suffix_array()

        return {
            "num_documents": len(self._documents),
            "text_length": len(self._text),
            "suffix_array_length": len(self._suffix_array),
            "num_unique_tokens": sum(len(tokens) for tokens in self._documents.values()),
        }


__all__ = ["SuffixArrayIndex"]
