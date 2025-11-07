import unittest

from src import ArrayScanIndex, InvertedIndex, SearchEngine, tokenize
from src.indexes.kgram_index import KGramIndex


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


if __name__ == "__main__":
    unittest.main()
