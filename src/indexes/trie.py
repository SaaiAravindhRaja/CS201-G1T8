"""Trie-based index for prefix searching."""

from __future__ import annotations

from typing import Dict, Optional, Sequence, Set

from .base import Index


class TrieNode:
    """Node in the trie structure."""
    
    def __init__(self) -> None:
        self.children: Dict[str, TrieNode] = {}
        self.doc_ids: Set[str] = set()


class TrieIndex(Index):
    """Trie-based index supporting prefix searches."""

    def __init__(self) -> None:
        self._root = TrieNode()

    def add_document(
        self,
        doc_id: str,
        tokens: Sequence[str],
    ) -> None:
        for token in set(tokens):
            self._insert_token(token, doc_id)

    def lookup_term(self, term: str) -> Set[str]:
        """Find documents containing terms that start with the given term."""
        node = self._find_node(term)
        if node is None:
            return set()
        return self._collect_all_docs(node)

    def _insert_token(self, token: str, doc_id: str) -> None:
        """Insert a token into the trie."""
        node = self._root
        for char in token:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.doc_ids.add(doc_id)

    def _find_node(self, prefix: str) -> Optional[TrieNode]:
        """Find the node corresponding to a prefix."""
        node = self._root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _collect_all_docs(self, node: TrieNode) -> Set[str]:
        """Collect all document IDs from this node and its subtree."""
        docs = set(node.doc_ids)
        for child in node.children.values():
            docs.update(self._collect_all_docs(child))
        return docs


__all__ = ["TrieIndex"]