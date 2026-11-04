#!/usr/bin/env python3
"""Check _ru_gloss_for_entry for kāiman with forced_case."""
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

# Original
tc.load_data(orig_dict, orig_ov, orig_pb, orig_pr, orig_pn)
for eid in ['new-kāiman', 2497]:
    entry = None
    for ee in tc._dictionary if hasattr(tc, '_dictionary') else []:
        pass
    # Can't access _dictionary, need to find entry another way
    # Let's use _pr_index
    matches = tc._pr_index.get('kāiman', [])
    for m_entry, label in matches:
        if str(m_entry.get('i')) == str(eid):
            ov = tc._override_by_id.get(m_entry.get('i'))
            gloss = tc._ru_gloss_for_entry(m_entry, label, forced_case='ablt')
            print(f'ORIG id={m_entry.get("i")} w={m_entry.get("w")} label={label} gloss_ablt={gloss}')

print()
# New
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))
matches = tc._pr_index.get('kāiman', [])
for m_entry, label in matches:
    if m_entry.get('i') in (11054, 2497):
        ov = tc._override_by_id.get(m_entry.get('i'))
        gloss = tc._ru_gloss_for_entry(m_entry, label, forced_case='ablt')
        print(f'NEW id={m_entry.get("i")} w={m_entry.get("w")} label={label} gloss_ablt={gloss}')
