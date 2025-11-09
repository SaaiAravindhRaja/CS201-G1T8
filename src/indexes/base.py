"""Abstract substring search contract shared by all implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Mapping, List


class Matcher(ABC):
    """Abstract data structure to standardize."""

    @abstractmethod
    def build(self, documents: Mapping[str, str]) -> None:
        """Ingest the full corpus as a mapping of ``doc_id -> raw text``."""

    @abstractmethod
    def lookup_term(self, term: str, doc_id: str) -> List[int]:
        """Return all positions (0-based) where ``term`` occurs in ``doc_id``."""


__all__ = ["Matcher"]
