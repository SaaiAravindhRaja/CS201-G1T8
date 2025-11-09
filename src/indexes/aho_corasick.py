"""Aho-Corasick automaton for multi-pattern substring search in one document.

This class integrates with the repo by exposing a Matcher-compatible API for
single-pattern lookups (fallback to str.find) and an additional patterns API:

    - build_patterns(patterns): compile the automaton for a list of patterns
    - match(doc_id): return [(pattern, position)] for all matches in a document

Use this for the single-doc, multi-pattern CLI where it shines.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from .base import Matcher
from ..text_utils import find_substring_positions


class AhoCorasick(Matcher):
    def __init__(self) -> None:
        # corpus storage (for convenience in CLI)
        self._doc_texts: Dict[str, str] = {}

        # automaton structures (built per pattern set)
        self._goto: List[Dict[str, int]] = []
        self._fail: List[int] = []
        self._out: List[List[int]] = []  # pattern indices per state
        self._patterns: List[str] = []

    # ----------------------------- corpus API --------------------------------
    def build(self, documents: Mapping[str, str]) -> None:
        self._doc_texts = {doc_id: (text or "").lower() for doc_id, text in documents.items()}

    # --------------------------- patterns API --------------------------------
    def build_patterns(self, patterns: Sequence[str]) -> None:
        self._patterns = [p.lower() for p in patterns if p]
        self._goto = [dict()]
        self._fail = [0]
        self._out = [[]]

        # build trie
        for pid, pat in enumerate(self._patterns):
            state = 0
            for ch in pat:
                nxt = self._goto[state].get(ch)
                if nxt is None:
                    nxt = len(self._goto)
                    self._goto.append({})
                    self._fail.append(0)
                    self._out.append([])
                    self._goto[state][ch] = nxt
                state = nxt
            self._out[state].append(pid)

        # build fail links (BFS)
        from collections import deque

        q: deque[int] = deque()
        for ch, s in self._goto[0].items():
            q.append(s)
            self._fail[s] = 0

        while q:
            r = q.popleft()
            for ch, s in self._goto[r].items():
                q.append(s)
                f = self._fail[r]
                while f and ch not in self._goto[f]:
                    f = self._fail[f]
                self._fail[s] = self._goto[f].get(ch, 0)
                # merge outputs
                self._out[s].extend(self._out[self._fail[s]])

    def match(self, doc_id: str) -> List[Tuple[str, int]]:
        """Return all (pattern, position) matches in the given document."""
        text = self._doc_texts.get(doc_id, "")
        if not text or not self._patterns:
            return []
        state = 0
        results: List[Tuple[str, int]] = []
        for i, ch in enumerate(text):
            while state and ch not in self._goto[state]:
                state = self._fail[state]
            state = self._goto[state].get(ch, 0)
            if self._out[state]:
                for pid in self._out[state]:
                    pat = self._patterns[pid]
                    results.append((pat, i - len(pat) + 1))
        return results

    # ------------------------ Matcher compatibility --------------------------
    def lookup_term(self, term: str, doc_id: str) -> List[int]:
        """Single-pattern convenience: enumerate positions in one doc."""
        term_lower = term.lower()
        text = self._doc_texts.get(doc_id, "")
        return find_substring_positions(text, term_lower)


__all__ = ["AhoCorasick"]
