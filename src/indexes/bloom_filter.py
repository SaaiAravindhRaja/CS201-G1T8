"""Bloom Filter index for probabilistic term lookup with space-time tradeoff."""

from __future__ import annotations

import hashlib
from typing import Sequence, Set

from .base import Index


class BloomFilterIndex(Index):

    def __init__(self, size: int = 1_000_000, num_hashes: int = 3) -> None:
        """
        Initialize bloom filter.
        
        Args:
            size: Bit array size (larger = fewer false positives, more memory)
            num_hashes: Number of hash functions (more = fewer false positives, slower)
        """
        self._size = size
        self._num_hashes = num_hashes
        self._bits = [False] * size
        self._documents: dict[str, set[str]] = {}  # Store docs for verification

    def add_document(
        self,
        doc_id: str,
        tokens: Sequence[str],
    ) -> None:
        """
        Add document to bloom filter and verification storage.
        
        Time: O(m·k) where m = unique tokens, k = num_hashes
        """
        # Store document tokens for verification phase
        token_set = set(tokens)
        self._documents[doc_id] = token_set
        
        # Add each token to bloom filter by setting k bits
        for token in token_set:
            for i in range(self._num_hashes):
                hash_val = self._hash(token, i)
                self._bits[hash_val] = True

    def _hash(self, term: str, seed: int) -> int:
        """
        Generate hash value for term using MD5 with seed.
        
        Returns: Integer in range [0, size)
        """
        hash_input = f"{term}:{seed}".encode()
        hash_hex = hashlib.md5(hash_input).hexdigest()
        return int(hash_hex, 16) % self._size

    def lookup_term(self, term: str) -> Set[str]:
        """
        Two-phase lookup demonstrating probabilistic data structure behavior.
        
        Phase 1: Bloom filter check - O(k)
        - Check if all k bits are set
        - If ANY bit is 0 → term DEFINITELY not present → return empty (FAST!)
        
        Phase 2: Verification scan - O(n·m)  
        - If ALL bits are 1 → term MAYBE present (could be false positive)
        - Must scan all documents to verify (SLOW!)
        
        This creates VARIABLE performance unlike O(1) hash lookup:
        - Rare terms: 0.001ms (bloom says NO)
        - Common terms: 8-10ms (bloom says MAYBE, must verify)
        """
        # Phase 1: Bloom filter negative check
        for i in range(self._num_hashes):
            hash_val = self._hash(term, i)
            if not self._bits[hash_val]:
                # Definitely not present! Fast path.
                return set()
        
        # Phase 2: Bloom filter says "maybe present"
        # Could be true positive OR false positive
        # Must verify by scanning all documents
        result = set()
        for doc_id, tokens in self._documents.items():
            if term in tokens:
                result.add(doc_id)
        
        return result

    def get_statistics(self) -> dict:
        """
        Calculate bloom filter statistics for analysis.
        
        Returns metrics useful for understanding performance:
        - bits_set: Number of bits set to 1
        - load_factor: Fraction of bits set (higher = more collisions)
        - theoretical_fpr: Expected false positive rate
        """
        bits_set = sum(self._bits)
        load_factor = bits_set / self._size
        
        # Theoretical false positive rate: (bits_set / size)^k
        theoretical_fpr = load_factor ** self._num_hashes
        
        return {
            "size": self._size,
            "num_hashes": self._num_hashes,
            "bits_set": bits_set,
            "load_factor": load_factor,
            "theoretical_fpr": theoretical_fpr,
            "num_documents": len(self._documents),
        }


__all__ = ["BloomFilterIndex"]
