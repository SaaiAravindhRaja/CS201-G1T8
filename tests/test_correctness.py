#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
from src.engine import SearchEngine
from src.indexes import ArrayScanIndex, InvertedIndex, BloomFilterIndex, KGramIndex, SuffixArrayIndex
from src.corpus import iter_reviews_from_csv
from pathlib import Path
from itertools import islice

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load small corpus
records = list(islice(iter_reviews_from_csv(Path('data/raw/airline.csv'), 'airline'), 100))

# Build exact-match indexes
exact_engines = {
    'ArrayScan': SearchEngine(ArrayScanIndex()),
    'Inverted': SearchEngine(InvertedIndex()),
    'Bloom': SearchEngine(BloomFilterIndex())
}

# Build substring-match indexes
substring_engines = {
    'KGram': SearchEngine(KGramIndex(k=3)),
    'SuffixArray': SearchEngine(SuffixArrayIndex())
}

# Add documents to all engines
for name, engine in exact_engines.items():
    for doc_id, text in records:
        engine.add_document(doc_id, text)

for name, engine in substring_engines.items():
    for doc_id, text in records:
        engine.add_document(doc_id, text)

# Test queries for exact matching
exact_test_queries = [
    ('Single term', 'flight', 'and'),
    ('AND query', 'flight comfortable', 'and'),
    ('OR query', 'flight comfortable', 'or'),
]

# Test queries for substring matching (only KGram and SuffixArray support this)
substring_test_queries = [
    ('Substring match', 'comf', 'and'),
    ('Prefix match', 'fli', 'and'),
]

print('Testing Correctness of Exact-Match Indexes')
print('='*60)

for query_name, query, mode in exact_test_queries:
    results = {}
    for name, engine in exact_engines.items():
        docs = engine.search(query, match_mode=mode)
        results[name] = set(d.doc_id for d in docs)

    print(f'\n{query_name}: "{query}" (mode={mode})')
    print(f'  ArrayScan: {len(results["ArrayScan"])} results')
    print(f'  Inverted:  {len(results["Inverted"])} results')
    print(f'  Bloom:     {len(results["Bloom"])} results')

    # Check correctness - all exact-match indexes should agree
    if results['ArrayScan'] == results['Inverted'] == results['Bloom']:
        print('  [OK] ALL MATCH - All exact-match indexes are CORRECT')
    else:
        print('  [FAIL] MISMATCH!')
        baseline = results['ArrayScan']
        for name in ['Inverted', 'Bloom']:
            if results[name] != baseline:
                extra = len(results[name] - baseline)
                missing = len(baseline - results[name])
                print(f'     {name}: {extra} extra, {missing} missing')

print('\n' + '='*60)
print('\nTesting Substring-Match Indexes (KGram and SuffixArray)')
print('='*60)
print('\nNote: Substring indexes may find more results than exact-match')
print('      indexes for queries that appear as substrings.')

for query_name, query, mode in substring_test_queries:
    results = {}
    # Test substring matching indexes
    for name in ['KGram', 'SuffixArray']:
        engine = substring_engines[name]
        docs = engine.search(query, match_mode=mode)
        results[name] = set(d.doc_id for d in docs)

    print(f'\n{query_name}: "{query}" (mode={mode})')
    print(f'  KGram:       {len(results["KGram"])} results')
    print(f'  SuffixArray: {len(results["SuffixArray"])} results')

    # Check that KGram and SuffixArray agree on substring matches
    if results['KGram'] == results['SuffixArray']:
        print('  [OK] MATCH - Both substring indexes agree')
    else:
        print('  [WARN] MISMATCH between KGram and SuffixArray')
        extra_kgram = len(results['KGram'] - results['SuffixArray'])
        extra_suffix = len(results['SuffixArray'] - results['KGram'])
        print(f'     KGram has {extra_kgram} extra, SuffixArray has {extra_suffix} extra')

# Test that substring indexes also work correctly for exact matches
print('\n' + '='*60)
print('\nVerifying Substring Indexes for Exact Match Queries')
print('='*60)

for query_name, query, mode in exact_test_queries:
    results = {}
    for name in ['KGram', 'SuffixArray']:
        engine = substring_engines[name]
        docs = engine.search(query, match_mode=mode)
        results[name] = set(d.doc_id for d in docs)

    print(f'\n{query_name}: "{query}" (mode={mode})')
    print(f'  KGram:       {len(results["KGram"])} results')
    print(f'  SuffixArray: {len(results["SuffixArray"])} results')

    if results['KGram'] == results['SuffixArray']:
        print('  [OK] Both substring indexes agree')
    else:
        print('  [WARN] Mismatch between substring indexes')

print('\n' + '='*60)
