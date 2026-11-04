#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

d = json.load(open(f'{ROOT}/data/dictionary.json', encoding='utf-8'))
for e in d:
    if e.get('i') == 10991:
        print(f'id=10991: w={e.get("w")} l={e.get("l")} ru={e.get("ru","")[:50]} s={e.get("s","")[:30]}')
    if e.get('i') == 8985:
        print(f'id=8985: w={e.get("w")} l={e.get("l")} ru={e.get("ru","")[:50]} s={e.get("s","")[:30]}')
