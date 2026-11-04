#!/usr/bin/env python3
"""Compare standalone translation of kāiman and warewīngi in orig vs new."""
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

# Test original
tc.load_data(orig_dict, orig_ov, orig_pb, orig_pr, orig_pn)
for w in ['kāiman', 'warewīngi', 'kāims']:
    r = json.loads(tc.translate_pr_sentence_json(w))
    print(f'ORIG {w}: {r["translation"]}')

print()

# Test new
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))
for w in ['kāiman', 'warewīngi', 'kāims']:
    r = json.loads(tc.translate_pr_sentence_json(w))
    print(f'NEW {w}: {r["translation"]}')
