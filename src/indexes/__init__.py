"""Collection of interchangeable substring search implementations."""

from .base import Matcher
from .array_scan import KMP
from .kgram_index import KGram
from .suffix_array import SuffixArray
from .suffix_array_logsq import SuffixArrayLogSq
from .aho_corasick import AhoCorasick

__all__ = [
    "Matcher",
    "KMP",
    "KGram",
    "SuffixArray",
    "SuffixArrayLogSq",
    "AhoCorasick",
]
