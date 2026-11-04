#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

# _pr_index contains (entry, label) tuples indexed by word form
# Find all entries for 'kāiman'
for key in ['kāiman']:
    matches = tc._pr_index.get(key, [])
    print(f'pr_index["{key}"]: {len(matches)} matches')
    for entry, label in matches:
        eid = entry.get('i')
        ov = tc._override_by_id.get(eid)
        pos = tc.classify_pos(entry, ov)
        has_ru = tc._entry_has_ru_gloss(entry)
        is_x = bool(entry.get('x'))
        score = (
            not has_ru,
            0,  # pos_miss
            0,  # verb_miss
            label != '',
            is_x,
        )
        print(f'  id={eid} w={entry.get("w")} ru={entry.get("ru")} label={label} pos={pos} score={score}')

print()
# Same for warewīngi
for key in ['warewīngi']:
    matches = tc._pr_index.get(key, [])
    print(f'pr_index["{key}"]: {len(matches)} matches')
    for entry, label in matches:
        eid = entry.get('i')
        ov = tc._override_by_id.get(eid)
        pos = tc.classify_pos(entry, ov)
        has_ru = tc._entry_has_ru_gloss(entry)
        is_x = bool(entry.get('x'))
        score = (
            not has_ru,
            0,  # pos_miss
            0,  # verb_miss
            label != '',
            is_x,
        )
        print(f'  id={eid} w={entry.get("w")} ru={entry.get("ru")} label={label} pos={pos} score={score}')
