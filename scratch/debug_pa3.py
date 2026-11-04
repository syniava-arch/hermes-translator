#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

# Check _pr_preposition_senses for pa
senses = tc._pr_preposition_senses.get('pa', [])
print(f'pa senses: {len(senses)}')
for s in senses:
    eid = s['entry'].get('i')
    gov = s['gov']
    ru = s['entry'].get('ru', '')
    print(f'  id={eid} gov={gov} ru={ru}')

# Check _select_pr_preposition_sense for different cases
for case in ['gen', 'dat', 'acc', None]:
    result = tc._select_pr_preposition_sense('pa', case, None)
    if result:
        eid = result[0].get('i')
        label = result[1]
        print(f'_select_pr_preposition_sense("pa", {case}) -> id={eid} label={label}')
