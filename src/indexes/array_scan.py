"""Naive baseline for substring search by scanning raw document text."""

from __future__ import annotations
from typing import Dict, Mapping, List
from .base import Matcher


class KMP(Matcher):
    """
    Baseline ``O(|dataset| + |input|)`` substring scan over raw texts for every query.
    """

    def __init__(self) -> None:
        self._texts: Dict[str, str] = {}

    def build(self, documents: Mapping[str, str]) -> None:
        self._texts = {doc_id: (text or "").lower() for doc_id, text in documents.items()}

    def lookup_term(self, term: str, doc_id: str) -> List[int]:
        pat = term.lower()
        if not pat:
            return []
        text = self._texts.get(doc_id, "")
        return self._kmp_all(text, pat)

    def _kmp_all(self, text: str, pat: str) -> List[int]:
        lps = self._kmp_lps(pat)
        i = 0
        j = 0
        res: List[int] = []
        n = len(text)
        m = len(pat)
        while i < n:
            if text[i] == pat[j]:
                i += 1
                j += 1
                if j == m:
                    res.append(i - j)
                    j = lps[j - 1]
            else:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
        return res

    def _kmp_lps(self, pat: str) -> List[int]:
        lps = [0] * len(pat)
        length = 0
        i = 1
        while i < len(pat):
            if pat[i] == pat[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps


__all__ = ["KMP"]
