#!/usr/bin/env python3
"""Trace sentence translation for 'pa Teutōtiskas ōrdenas'."""
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

# Trace the translation
result = tc.translate_pr_sentence_json("pa Teutōtiskas ōrdenas")
print(f'Input: pa Teutōtiskas ōrdenas')
print(f'Output: {result["text"]}')
print(f'Words:')
for w in result.get('words', []):
    print(f'  src={w["src"]} out={w["out"]} note={w.get("note","")}')
