#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

result = json.loads(tc.translate_pr_sentence_json('pa Teutōtiskas ōrdenas'))
print(f'Output: {result["translation"]}')
for w in result.get('words', []):
    print(f'  {w}')
