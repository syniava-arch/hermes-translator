#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

matches = tc._lookup_pr_matches('kāiman')
print(f'NEW kāiman matches: {len(matches)}')
for m in matches[:5]:
    print(f'  id={m[0].get("i")}, w={m[0].get("w")}, ru={m[0].get("ru")}, label={m[1]}')

# Score them
selected = tc._select_pr_match('kāiman')
if selected:
    entry, label = selected
    print(f'SELECTED: id={entry.get("i")}, w={entry.get("w")}, label={label}')

# Check warewīngi
matches2 = tc._lookup_pr_matches('warewīngi')
print(f'NEW warewīngi matches: {len(matches2)}')
for m in matches2[:5]:
    print(f'  id={m[0].get("i")}, w={m[0].get("w")}, ru={m[0].get("ru")}, label={m[1]}')

selected2 = tc._select_pr_match('warewīngi')
if selected2:
    entry, label = selected2
    print(f'SELECTED: id={entry.get("i")}, w={entry.get("w")}, label={label}')
