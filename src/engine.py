"""Search engine orchestrating tokenization, indexing, and matching."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Set

from .indexes import Index
from .tokenizer import tokenize


@dataclass
class Document:
    doc_id: str
    text: str


class SearchEngine:
    """Lightweight engine for AND/OR keyword matching."""

    def __init__(self, index: Index) -> None:
        self._index = index
        self._documents: Dict[str, Document] = {}

    def add_document(self, doc_id: str, text: str) -> None:
        tokens = tokenize(text)
        self._index.add_document(doc_id, tokens)
        self._documents[doc_id] = Document(doc_id=doc_id, text=text)

    def search(self, query: str, *, match_mode: str = "and") -> Sequence[Document]:
        tokens = tokenize(query)
        if not tokens:
            return []
        match_mode = match_mode.lower()
        if match_mode not in {"and", "or"}:
            raise ValueError("match_mode must be 'and' or 'or'")
        matching_ids = self._match_tokens(tokens, match_mode)
        return [self._documents[doc_id] for doc_id in matching_ids if doc_id in self._documents]

    def documents(self) -> Iterable[Document]:
        return self._documents.values()

    # Internal helpers -------------------------------------------------

    def _match_tokens(self, tokens: Sequence[str], match_mode: str) -> List[str]:
        matching: Set[str]
        if match_mode == "and":
            matching = self._index.lookup_term(tokens[0])
            for token in tokens[1:]:
                matching &= self._index.lookup_term(token)
                if not matching:
                    break
        else:  # OR mode
            matching = set()
            for token in tokens:
                matching |= self._index.lookup_term(token)
        return sorted(matching)


__all__ = ["SearchEngine", "Document"]
