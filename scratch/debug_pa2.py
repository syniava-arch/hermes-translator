#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

# Check what _next_pr_case returns for 'pa Teutōtiskas'
tokens = ['pa', 'teutōtiskas']
for i, tok in enumerate(tokens):
    clean = tc._clean_pr_token(tok)
    if clean in tc._preposition_index or tc._preposition_key(clean):
        next_case = tc._next_pr_case(tokens, i)
        print(f'next_case after "{tok}" (idx={i}) = {next_case}')

# Check _select_pr_preposition_sense for 'pa' with next_case='gen'
sense = tc._select_pr_preposition_sense('pa', 'gen', None)
print(f'_select_pr_preposition_sense("pa", "gen") = {sense}')
