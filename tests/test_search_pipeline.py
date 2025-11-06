import unittest

from src import ArrayScanIndex, InvertedIndex, SearchEngine, tokenize


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


if __name__ == "__main__":
    unittest.main()
