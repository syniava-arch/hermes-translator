#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

# Check _select_pr_match for 'pa'
m = tc._select_pr_match('pa')
print(f'_select_pr_match("pa") = id={m[0].get("i")} w={m[0].get("w")} ru={m[0].get("ru","")}')

# Check _pr_preposition_senses for pa
senses = tc._pr_preposition_senses.get('pa', [])
print(f'pa senses count: {len(senses)}')
for s in senses:
    print(f'  id={s["entry"].get("i")} gov={s["gov"]} ru={s["entry"].get("ru","")[:30]}')

# Check _pr_to_ru_priority for pa
print(f'pr_to_ru priority for pa: {tc._pr_to_ru_priority.get("pa")}')
