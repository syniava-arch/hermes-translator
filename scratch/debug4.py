#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

# Check classify_pos for kāims (2497) and kāiman (11054)
for eid in [2497, 11054]:
    for ee in tc._dictionary:
        if ee.get('i') == eid:
            ov = tc._override_by_id.get(eid)
            pos = tc.classify_pos(ee, ov)
            has_ru = tc._entry_has_ru_gloss(ee)
            print(f'id={eid} w={ee.get("w")} pos={pos} has_ru={has_ru} override_keys={list(ov.keys()) if ov else None}')
            break

# Check _select_pr_match scores manually
for eid in [2497, 11054]:
    for ee in tc._dictionary:
        if ee.get('i') == eid:
            ov = tc._override_by_id.get(eid)
            pos = tc.classify_pos(ee, ov)
            # Simulate HEAD score
            is_cross_ref = bool(ee.get('x'))
            label = '' if eid == 11054 else 'masc.sg.akk'
            score = (
                not tc._entry_has_ru_gloss(ee),
                0,  # pos_miss
                0,  # verb_miss
                label != '',
                is_cross_ref,
            )
            print(f'  score for id={eid} label={label}: {score}')
            break

# Check what _select_pr_match returns
for word in ['kāiman', 'warewīngi']:
    m = tc._select_pr_match(word, prefer_pos=None)
    if m:
        print(f'SELECTED {word}: id={m[0].get("i")}, w={m[0].get("w")}, label={m[1]}')
