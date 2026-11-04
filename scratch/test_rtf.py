#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

# Test pa with genitive
for sent in ['pa Teutōtiskas ōrdenas', 'Pa Teutōtiskas ōrdenas legēndans', 'pa Teutōtiskas']:
    r = json.loads(tc.translate_pr_sentence_json(sent))
    print(f'pa: {sent}')
    print(f'  -> {r["translation"]}')
    for w in r['words']:
        print(f'     {w}')
    print()

# Test aulaūwuns as participle
for sent in ['Ērks Mānts aulaūwuns', 'Ērks Mānts aulaūwuns en 1273 mettan']:
    r = json.loads(tc.translate_pr_sentence_json(sent))
    print(f'aula: {sent}')
    print(f'  -> {r["translation"]}')
    for w in r['words']:
        print(f'     {w}')
    print()

# Test standalone
for w in ['aulaūwuns', 'aulaūwusi', 'aulaūwusins']:
    r = json.loads(tc.translate_pr_sentence_json(w))
    print(f'{w}: {r["translation"]}')
