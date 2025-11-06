"""Abstract index contract shared by all concrete backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence, Set


class Index(ABC):
    """Abstract index contract required by :class:`SearchEngine`."""

    @abstractmethod
    def add_document(
        self,
        doc_id: str,
        tokens: Sequence[str],
    ) -> None:
        """Insert one document into the index."""

    @abstractmethod
    def lookup_term(self, term: str) -> Set[str]:
        """Return doc IDs that contain ``term``."""


__all__ = ["Index"]
