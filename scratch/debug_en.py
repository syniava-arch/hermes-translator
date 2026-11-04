#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

# Check classify_pos for 'en'
for w in ['en', '1273', 'mettan']:
    m = tc._select_pr_match(w)
    if m:
        pos = tc.classify_pos(m[0], m[1])
        print(f'{w}: _select_pr_match -> id={m[0].get("i")} pos={pos} label={m[1]!r}')
    else:
        print(f'{w}: _select_pr_match -> None')

# Also check what _next_pr_case returns for 'en' followed by '1273'
next_case = tc._next_pr_case(['en', '1273', 'mettan'], 0)
print(f'_next_pr_case(["en","1273","mettan"], 0) = {next_case}')

# And _ru_case_after_pr_preposition
ru_case = tc._ru_case_after_pr_preposition('en', next_case)
print(f'_ru_case_after_pr_preposition("en", {next_case}) = {ru_case}')
