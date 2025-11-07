#!/usr/bin/env python3
from src.engine import SearchEngine
from src.indexes import ArrayScanIndex, InvertedIndex, BloomFilterIndex
from src.corpus import iter_reviews_from_csv
from pathlib import Path
from itertools import islice

# Load small corpus
records = list(islice(iter_reviews_from_csv(Path('data/raw/airline.csv'), 'airline'), 100))

# Build all three indexes
engines = {
    'ArrayScan': SearchEngine(ArrayScanIndex()),
    'Inverted': SearchEngine(InvertedIndex()),
    'Bloom': SearchEngine(BloomFilterIndex())
}

for name, engine in engines.items():
    for doc_id, text in records:
        engine.add_document(doc_id, text)

# Test queries
test_queries = [
    ('Single term', 'flight', 'and'),
    ('AND query', 'flight comfortable', 'and'),
    ('OR query', 'flight comfortable', 'or'),
]

print('Testing Correctness of BloomFilter')
print('='*60)

for query_name, query, mode in test_queries:
    results = {}
    for name, engine in engines.items():
        docs = engine.search(query, match_mode=mode)
        results[name] = set(d.doc_id for d in docs)
    
    print(f'\n{query_name}: "{query}" (mode={mode})')
    print(f'  ArrayScan:  {len(results["ArrayScan"])} results')
    print(f'  Inverted:   {len(results["Inverted"])} results')
    print(f'  Bloom:      {len(results["Bloom"])} results')
    
    # Check correctness
    if results['ArrayScan'] == results['Inverted'] == results['Bloom']:
        print('  ✅ ALL MATCH - BloomFilter is CORRECT')
    else:
        print('  ❌ MISMATCH!')
        if results['ArrayScan'] != results['Bloom']:
            print(f'     ArrayScan vs Bloom: {len(results["ArrayScan"] - results["Bloom"])} extra in ArrayScan, {len(results["Bloom"] - results["ArrayScan"])} extra in Bloom')
        if results['Inverted'] != results['Bloom']:
            print(f'     Inverted vs Bloom: {len(results["Inverted"] - results["Bloom"])} extra in Inverted, {len(results["Bloom"] - results["Inverted"])} extra in Bloom')

print('\n' + '='*60)
