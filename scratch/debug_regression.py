#!/usr/bin/env python3
import json, sys, os
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

for sent in ['Pakarwjas warē, warewīngi Ebwarē!', 'Prūsai sen Ērkun Māntan ebwarīwusis miksjans en Nātangai, prei Pakarwjas kāiman']:
    r = json.loads(tc.translate_pr_sentence_json(sent))
    print(f'Sentence: {sent}')
    print(f'Result: {r["translation"]}')
    for w in r['words']:
        if w.get('note') and '?' in w.get('note', ''):
            print(f'  WARN: {w}')
    print()

# Check Prūsai match
match = tc._select_pr_match('prūsai')
if match:
    entry, label = match
    print(f'Prūsai match: id={entry.get("i")}, w={entry.get("w")}, ru={entry.get("ru")}, label={label}')

# Check Ebwarē match
match2 = tc._select_pr_match('ebwarē')
if match2:
    entry, label = match2
    print(f'Ebwarē match: id={entry.get("i")}, w={entry.get("w")}, ru={entry.get("ru")}, label={label}')
