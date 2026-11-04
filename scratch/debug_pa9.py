#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

senses = tc._pr_preposition_senses.get('pa', [])
for s in senses:
    e = s['entry']
    g, n = tc._ru_gloss_for_entry(e, '')
    g2, n2 = tc._ru_gloss_for_entry(e, '', forced_case='datv')
    print(f'id={e.get("i")} gov={s["gov"]} ru={e.get("ru","")[:30]}')
    print(f'  _ru_gloss_for_entry(entry, "") = "{g}"')
    print(f'  _ru_gloss_for_entry(entry, "", forced_case="datv") = "{g2}"')
