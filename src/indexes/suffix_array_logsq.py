"""Reference suffix array index built with O(n log^2 n) prefix-doubling."""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence, Set

from .base import Matcher


class SuffixArrayLogSq(Matcher):
    """
    Suffix Array but O(n log^2 n) for building, using existing sort function.
    """

    _SEPARATOR = "\x00"

    def __init__(self) -> None:
        self._doc_texts: Dict[str, str] = {}
        self._text: str = ""
        self._suffix_array: List[int] = []
        self._position_doc_ids: List[Optional[str]] = []
        self._position_offsets: List[int] = []

    def build(self, documents: Mapping[str, str]) -> None:
        self._doc_texts = {}
        self._text = ""
        self._suffix_array = []
        self._position_doc_ids = []
        self._position_offsets = []

        text_parts: List[str] = []
        position_docs: List[Optional[str]] = []
        position_offsets: List[int] = []

        for doc_id, text in documents.items():
            text_lower = text.lower()
            if not text_lower:
                continue
            self._doc_texts[doc_id] = text_lower
            off = 0
            for ch in text_lower:
                text_parts.append(ch)
                position_docs.append(doc_id)
                position_offsets.append(off)
                off += 1
            text_parts.append(self._SEPARATOR)
            position_docs.append(None)
            position_offsets.append(-1)

        if not text_parts:
            return

        self._text = "".join(text_parts)
        self._position_doc_ids = position_docs
        self._position_offsets = position_offsets
        self._suffix_array = self._build_suffix_array(self._text)

    # token normalization removed in raw-text design

    def _build_suffix_array(self, text: str) -> List[int]:
        n = len(text)
        if n == 0:
            return []

        sa = list(range(n))
        rank = [ord(c) for c in text]
        tmp_rank = [0] * n
        k = 1

        while True:
            sa.sort(key=lambda i: (rank[i], rank[i + k] if i + k < n else -1))
            tmp_rank[sa[0]] = 0
            for i in range(1, n):
                prev = sa[i - 1]
                curr = sa[i]
                prev_pair = (rank[prev], rank[prev + k] if prev + k < n else -1)
                curr_pair = (rank[curr], rank[curr + k] if curr + k < n else -1)
                tmp_rank[curr] = tmp_rank[prev] + (curr_pair != prev_pair)
            rank, tmp_rank = tmp_rank, rank
            if rank[sa[-1]] == n - 1:
                break
            k <<= 1

        return sa

    def lookup_term(self, term: str, doc_id: str) -> List[int]:
        if not self._suffix_array or not term:
            return []

        pattern = term.lower()
        left = self._lower_bound(pattern)
        right = self._upper_bound(pattern)
        if left == right:
            return []

        positions: List[int] = []
        for idx in range(left, right):
            pos = self._suffix_array[idx]
            d = self._position_doc_ids[pos]
            if d == doc_id:
                positions.append(self._position_offsets[pos])
        return positions

    # candidate-doc utility removed; return positions directly

    def _lower_bound(self, pattern: str) -> int:
        left, right = 0, len(self._suffix_array)
        while left < right:
            mid = (left + right) // 2
            if self._compare_suffix(mid, pattern) < 0:
                left = mid + 1
            else:
                right = mid
        return left

    def _upper_bound(self, pattern: str) -> int:
        left, right = 0, len(self._suffix_array)
        pattern_upper = pattern + "\uffff"
        while left < right:
            mid = (left + right) // 2
            if self._compare_suffix(mid, pattern_upper) < 0:
                left = mid + 1
            else:
                right = mid
        return left

    def _compare_suffix(self, sa_index: int, pattern: str) -> int:
        pos = self._suffix_array[sa_index]
        suffix = self._text[pos : pos + len(pattern)]
        if suffix == pattern:
            return 0
        return -1 if suffix < pattern else 1

    def get_statistics(self) -> dict:
        return {
            "num_documents": len(self._doc_texts),
            "text_length": len(self._text),
            "suffix_array_length": len(self._suffix_array),
            "num_unique_tokens": 0,
        }


__all__ = ["SuffixArrayLogSq"]
