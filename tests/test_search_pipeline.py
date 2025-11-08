import unittest

from src import ArrayScanIndex, InvertedIndex, SearchEngine, tokenize
from src.indexes.kgram_index import KGramIndex
from src.indexes.suffix_array import SuffixArrayIndex


class TokenizerTests(unittest.TestCase):
    def test_tokenize_basic(self) -> None:
        tokens = tokenize("Tight legroom & comfy seats 24/7!")
        self.assertEqual(tokens, ["tight", "legroom", "comfy", "seats", "24", "7"])


class SearchEngineTests(unittest.TestCase):
    SAMPLE_DOCS = {
        "airline:0": "Seats have tight legroom but the crew was friendly.",
        "airline:1": "Comfortable seats with great legroom and tasty meals.",
        "airline:2": "Spacious cabin yet uncomfortable legroom overall.",
    }

    def _build_engine(self, index_cls):
        engine = SearchEngine(index_cls())
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        return engine

    def test_and_mode(self) -> None:
        engine = self._build_engine(ArrayScanIndex)
        result_ids = [doc.doc_id for doc in engine.search("legroom comfortable", match_mode="and")]
        self.assertEqual(result_ids, ["airline:1"])

    def test_or_mode(self) -> None:
        engine = self._build_engine(InvertedIndex)
        result_ids = [doc.doc_id for doc in engine.search("tight spacious", match_mode="or")]
        self.assertEqual(sorted(result_ids), ["airline:0", "airline:2"])

    def test_and_short_circuit(self) -> None:
        engine = self._build_engine(InvertedIndex)
        result_ids = [doc.doc_id for doc in engine.search("legroom nonexistent", match_mode="and")]
        self.assertEqual(result_ids, [])


class KGramIndexTests(unittest.TestCase):
    """Test k-gram index substring matching behavior."""

    SAMPLE_DOCS = {
        "doc:0": "comfortable seating legroom",
        "doc:1": "discomfort with narrow legroom",
        "doc:2": "leg space",
    }

    def test_kgram_exact_match(self) -> None:
        """K-gram should match exact tokens like inverted index."""
        engine = SearchEngine(KGramIndex(k=3))
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Search for exact token "legroom"
        result_ids = [doc.doc_id for doc in engine.search("legroom", match_mode="and")]
        self.assertIn("doc:0", result_ids)
        self.assertIn("doc:1", result_ids)

    def test_kgram_substring_match(self) -> None:
        """K-gram should match substrings (distinct from exact matching)."""
        engine = SearchEngine(KGramIndex(k=3))
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Search for substring "comfort" (matches "comfortable" and "discomfort")
        result_ids = sorted([doc.doc_id for doc in engine.search("comfort", match_mode="and")])
        # Should return doc:0 (comfortable) and doc:1 (discomfort)
        self.assertEqual(result_ids, ["doc:0", "doc:1"])

    def test_kgram_short_query(self) -> None:
        """K-gram with query shorter than k should still work."""
        engine = SearchEngine(KGramIndex(k=3))
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Search for substring "leg" (shorter than k=3)
        result_ids = sorted([doc.doc_id for doc in engine.search("leg", match_mode="and")])
        # Should find doc:0 (legroom), doc:1 (legroom), and doc:2 (leg)
        self.assertEqual(result_ids, ["doc:0", "doc:1", "doc:2"])

    def test_kgram_no_match(self) -> None:
        """K-gram should return empty set for non-matching query."""
        engine = SearchEngine(KGramIndex(k=3))
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        result_ids = [doc.doc_id for doc in engine.search("xyz", match_mode="and")]
        self.assertEqual(result_ids, [])

    def test_kgram_multiple_word_query(self) -> None:
        """K-gram should handle multi-word queries in AND mode."""
        engine = SearchEngine(KGramIndex(k=3))
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Both "comfort" and "narrow" must match
        result_ids = [doc.doc_id for doc in engine.search("comfort narrow", match_mode="and")]
        self.assertEqual(result_ids, ["doc:1"])

    def test_kgram_or_mode(self) -> None:
        """K-gram should handle OR mode queries."""
        engine = SearchEngine(KGramIndex(k=3))
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Match either "comfort" or "space"
        result_ids = sorted([doc.doc_id for doc in engine.search("comfort space", match_mode="or")])
        self.assertEqual(result_ids, ["doc:0", "doc:1", "doc:2"])

    def test_kgram_prefix_match(self) -> None:
        """K-gram should support prefix matching."""
        engine = SearchEngine(KGramIndex(k=3))
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Search for prefix "seat" (matches "seating")
        result_ids = [doc.doc_id for doc in engine.search("seat", match_mode="and")]
        self.assertIn("doc:0", result_ids)

    def test_kgram_different_k_values(self) -> None:
        """Test k-gram with different k values."""
        # Test with k=2
        engine_k2 = SearchEngine(KGramIndex(k=2))
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine_k2.add_document(doc_id, text)
        result_ids = sorted([doc.doc_id for doc in engine_k2.search("com", match_mode="and")])
        self.assertEqual(result_ids, ["doc:0", "doc:1"])

        # Test with k=4
        engine_k4 = SearchEngine(KGramIndex(k=4))
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine_k4.add_document(doc_id, text)
        result_ids = sorted([doc.doc_id for doc in engine_k4.search("comf", match_mode="and")])
        self.assertEqual(result_ids, ["doc:0", "doc:1"])

    def test_kgram_case_insensitive(self) -> None:
        """K-gram should be case insensitive."""
        engine = SearchEngine(KGramIndex(k=3))
        engine.add_document("doc:test", "COMFORTABLE Seating")
        result_ids = [doc.doc_id for doc in engine.search("comfort", match_mode="and")]
        self.assertIn("doc:test", result_ids)
        result_ids = [doc.doc_id for doc in engine.search("SEAT", match_mode="and")]
        self.assertIn("doc:test", result_ids)

    def test_kgram_statistics(self) -> None:
        """Test k-gram statistics method."""
        index = KGramIndex(k=3)
        index.add_document("doc:0", ["comfortable", "seating"])
        stats = index.get_statistics()
        self.assertEqual(stats["k"], 3)
        self.assertGreater(stats["vocabulary_size"], 0)
        self.assertEqual(stats["num_documents"], 1)


class SuffixArrayIndexTests(unittest.TestCase):
    """Test suffix array index substring matching behavior."""

    SAMPLE_DOCS = {
        "doc:0": "comfortable seating legroom",
        "doc:1": "discomfort with narrow legroom",
        "doc:2": "leg space",
    }

    def test_suffix_array_exact_match(self) -> None:
        """Suffix array should match exact tokens."""
        engine = SearchEngine(SuffixArrayIndex())
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Search for exact token "legroom"
        result_ids = sorted([doc.doc_id for doc in engine.search("legroom", match_mode="and")])
        self.assertEqual(result_ids, ["doc:0", "doc:1"])

    def test_suffix_array_substring_match(self) -> None:
        """Suffix array should match substrings."""
        engine = SearchEngine(SuffixArrayIndex())
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Search for substring "comfort" (matches "comfortable" and "discomfort")
        result_ids = sorted([doc.doc_id for doc in engine.search("comfort", match_mode="and")])
        self.assertEqual(result_ids, ["doc:0", "doc:1"])

    def test_suffix_array_prefix_match(self) -> None:
        """Suffix array should support prefix matching."""
        engine = SearchEngine(SuffixArrayIndex())
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Search for prefix "seat" (matches "seating")
        result_ids = [doc.doc_id for doc in engine.search("seat", match_mode="and")]
        self.assertIn("doc:0", result_ids)

    def test_suffix_array_short_query(self) -> None:
        """Suffix array should handle short queries."""
        engine = SearchEngine(SuffixArrayIndex())
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Search for substring "leg"
        result_ids = sorted([doc.doc_id for doc in engine.search("leg", match_mode="and")])
        self.assertEqual(result_ids, ["doc:0", "doc:1", "doc:2"])

    def test_suffix_array_no_match(self) -> None:
        """Suffix array should return empty set for non-matching query."""
        engine = SearchEngine(SuffixArrayIndex())
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        result_ids = [doc.doc_id for doc in engine.search("xyz", match_mode="and")]
        self.assertEqual(result_ids, [])

    def test_suffix_array_multiple_word_query(self) -> None:
        """Suffix array should handle multi-word queries in AND mode."""
        engine = SearchEngine(SuffixArrayIndex())
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Both "comfort" and "narrow" must match
        result_ids = [doc.doc_id for doc in engine.search("comfort narrow", match_mode="and")]
        self.assertEqual(result_ids, ["doc:1"])

    def test_suffix_array_or_mode(self) -> None:
        """Suffix array should handle OR mode queries."""
        engine = SearchEngine(SuffixArrayIndex())
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Match either "comfort" or "space"
        result_ids = sorted([doc.doc_id for doc in engine.search("comfort space", match_mode="or")])
        self.assertEqual(result_ids, ["doc:0", "doc:1", "doc:2"])

    def test_suffix_array_case_insensitive(self) -> None:
        """Suffix array should be case insensitive."""
        engine = SearchEngine(SuffixArrayIndex())
        engine.add_document("doc:test", "COMFORTABLE Seating")
        result_ids = [doc.doc_id for doc in engine.search("comfort", match_mode="and")]
        self.assertIn("doc:test", result_ids)
        result_ids = [doc.doc_id for doc in engine.search("SEAT", match_mode="and")]
        self.assertIn("doc:test", result_ids)

    def test_suffix_array_single_character(self) -> None:
        """Suffix array should handle single character queries."""
        engine = SearchEngine(SuffixArrayIndex())
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        # Search for single character "l"
        result_ids = sorted([doc.doc_id for doc in engine.search("l", match_mode="and")])
        # All documents contain "l"
        self.assertEqual(result_ids, ["doc:0", "doc:1", "doc:2"])

    def test_suffix_array_lazy_rebuild(self) -> None:
        """Suffix array should rebuild lazily after adding documents."""
        index = SuffixArrayIndex()
        # Add document
        index.add_document("doc:0", ["test"])
        # Lookup should trigger rebuild
        result = index.lookup_term("test")
        self.assertIn("doc:0", result)
        # Add another document
        index.add_document("doc:1", ["testing"])
        # Lookup should rebuild and find both
        result = index.lookup_term("test")
        self.assertEqual(sorted(result), ["doc:0", "doc:1"])

    def test_suffix_array_statistics(self) -> None:
        """Test suffix array statistics method."""
        index = SuffixArrayIndex()
        index.add_document("doc:0", ["comfortable", "seating"])
        stats = index.get_statistics()
        self.assertEqual(stats["num_documents"], 1)
        self.assertGreater(stats["text_length"], 0)
        self.assertGreater(stats["suffix_array_length"], 0)
        self.assertEqual(stats["num_unique_tokens"], 2)

    def test_suffix_array_empty_query(self) -> None:
        """Suffix array should handle empty query."""
        engine = SearchEngine(SuffixArrayIndex())
        for doc_id, text in self.SAMPLE_DOCS.items():
            engine.add_document(doc_id, text)
        result_ids = [doc.doc_id for doc in engine.search("", match_mode="and")]
        self.assertEqual(result_ids, [])


if __name__ == "__main__":
    unittest.main()
