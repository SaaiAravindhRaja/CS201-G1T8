"""Search engine orchestrating tokenization, indexing, and matching."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .indexes import Matcher
from .text_utils import find_substring_positions


@dataclass
class Document:
    doc_id: str
    text: str


class SearchEngine:
    """Lightweight engine for AND/OR keyword matching."""

    def __init__(self, index: Matcher) -> None:
        self._index = index
        self._documents: Dict[str, Document] = {}
        self._normalized_texts: Dict[str, str] = {}
        self._built = False

    def build(self, documents: Iterable[Tuple[str, str]]) -> None:
        self._documents = {}
        self._normalized_texts = {}
        text_map: Dict[str, str] = {}
        for doc_id, raw_text in documents:
            text = raw_text or ""
            text_map[doc_id] = text
            self._documents[doc_id] = Document(doc_id=doc_id, text=text)
            self._normalized_texts[doc_id] = text.lower()
        self._index.build(text_map)
        self._built = True

    def search(self, query: str, *, match_mode: str = "and", doc_id: Optional[str] = None) -> Sequence[Document]:
        if not self._built:
            raise RuntimeError("SearchEngine.build() must be called before search().")
        tokens = [t for t in query.lower().split() if t]
        if not tokens:
            return []
        match_mode = match_mode.lower()
        if match_mode not in {"and", "or"}:
            raise ValueError("match_mode must be 'and' or 'or'")
        if doc_id is not None:
            text_lower = self._normalized_texts.get(doc_id)
            if text_lower is None:
                return []
            positions = find_substring_positions(text_lower, query.lower())
            return positions  # type: ignore[return-value]

        matching_ids = self._match_tokens(tokens, match_mode)
        return [self._documents[doc_id] for doc_id in matching_ids if doc_id in self._documents]

    def documents(self) -> Iterable[Document]:
        return self._documents.values()

    def _match_tokens(self, tokens: Sequence[str], match_mode: str) -> List[str]:
        match_all = match_mode == "and"
        matching: List[str] = []
        for doc_id in self._documents:
            if match_all:
                if all(self._index.lookup_term(token, doc_id) for token in tokens):
                    matching.append(doc_id)
            else:
                if any(self._index.lookup_term(token, doc_id) for token in tokens):
                    matching.append(doc_id)
        return matching


__all__ = ["SearchEngine", "Document"]
