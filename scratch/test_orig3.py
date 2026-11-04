#!/usr/bin/env python3
"""Test with original data to see _pr_index for kāiman."""
import json, sys, subprocess
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)

def git_show(path):
    r = subprocess.run(['git', 'show', 'b90776f:' + path], capture_output=True, text=True, cwd=ROOT)
    return r.stdout

orig_dict = git_show('data/dictionary.json')
orig_ov = git_show('data/overrides.json')
orig_pb = git_show('data/phrasebook.json')
orig_pr = git_show('data/priorities.json')
orig_pn = git_show('data/propernames.json')

import translate_core as tc
tc.load_data(orig_dict, orig_ov, orig_pb, orig_pr, orig_pn)

for key in ['kāiman', 'warewīngi']:
    matches = tc._pr_index.get(key, [])
    print(f'ORIG pr_index["{key}"]: {len(matches)} matches')
    for entry, label in matches:
        eid = entry.get('i')
        ov = tc._override_by_id.get(eid)
        pos = tc.classify_pos(entry, ov)
        has_ru = tc._entry_has_ru_gloss(entry)
        is_x = bool(entry.get('x'))
        score = (
            not has_ru,
            0,
            0,
            label != '',
            is_x,
        )
        print(f'  id={eid} w={entry.get("w")} ru={entry.get("ru")} label={label} pos={pos} score={score}')
