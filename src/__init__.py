"""Lightweight search package implementing shared tokenizer, indices, and engine."""

from .tokenizer import tokenize
from .indexes import Index, ArrayScanIndex, InvertedIndex
from .engine import SearchEngine

__all__ = [
    "tokenize",
    "Index",
    "ArrayScanIndex",
    "InvertedIndex",
    "SearchEngine",
]
