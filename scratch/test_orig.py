#!/usr/bin/env python3
"""Test with original b90776f data to see if kāiman/warewīngi worked before."""
import json, sys, subprocess
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)

# Load original data from git
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

for sent in ['Pakarwjas warē, warewīngi Ebwarē!', 'Prūsai sen Ērkun Māntan ebwarīwusis miksjans en Nātangai, prei Pakarwjas kāiman']:
    r = json.loads(tc.translate_pr_sentence_json(sent))
    print(f'ORIG: {r["translation"]}')

# Check if kāiman was in original dictionary
d = json.loads(orig_dict)
for e in d:
    if (e.get('w') or '').lower() == 'kāiman':
        print(f'ORIG dict kāiman: id={e.get("i")}, ru={e.get("ru")}')

# Check lookup for kāiman in original
matches = tc._lookup_pr_matches('kāiman')
print(f'ORIG kāiman matches: {len(matches)}')
for m in matches[:3]:
    print(f'  id={m[0].get("i")}, w={m[0].get("w")}, ru={m[0].get("ru")}, label={m[1]}')
