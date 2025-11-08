"""Collection of interchangeable index implementations."""

from .base import Index
from .array_scan import ArrayScanIndex
from .inverted import InvertedIndex
from .bloom_filter import BloomFilterIndex
from .kgram_index import KGramIndex
from .suffix_array import SuffixArrayIndex

__all__ = ["Index", "ArrayScanIndex", "InvertedIndex", "BloomFilterIndex", "KGramIndex", "SuffixArrayIndex"]
