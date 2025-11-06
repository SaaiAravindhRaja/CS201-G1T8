"""Collection of interchangeable index implementations."""

from .base import Index
from .array_scan import ArrayScanIndex
from .inverted import InvertedIndex

__all__ = ["Index", "ArrayScanIndex", "InvertedIndex"]
