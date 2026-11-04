#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

# Check the mapping
result = tc._ru_case_after_pr_preposition('pa', 'gen')
print(f'_ru_case_after_pr_preposition("pa", "gen") = {result}')

# Check for Teutōtiskas
matches = tc._lookup_pr_matches('teutōtiskas')
print(f'Teutōtiskas matches: {len(matches)}')
for entry, label in matches[:3]:
    print(f'  id={entry.get("i")} w={entry.get("w")} label={label}')

# Check what case is detected
m = tc._select_pr_match('teutōtiskas')
if m:
    entry, label = m
    info = tc._label_grammar(label)
    print(f'Selected: id={entry.get("i")} label={label}')
    print(f'  label_grammar: {info}')
