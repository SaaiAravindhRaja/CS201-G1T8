"""Lightweight substring search package: implementations and engine."""

from .indexes import (
    Matcher,
    KMP,
    KGram,
    SuffixArray,
    SuffixArrayLogSq,
    AhoCorasick,
)
from .engine import SearchEngine

__all__ = [
    "Matcher",
    "KMP",
    "KGram",
    "SuffixArray",
    "SuffixArrayLogSq",
    "AhoCorasick",
    "SearchEngine",
]
