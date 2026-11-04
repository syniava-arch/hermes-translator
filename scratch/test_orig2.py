#!/usr/bin/env python3
"""Run tests with ORIGINAL b90776f data to verify it passed."""
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

# Run just the two failing tests
cases = [
    ("power-victory", "Pakarwjas warē, warewīngi Ebwarē!", "Покарвис мощь, могучая Победа!"),
    ("prussians-win", "Prūsai sen Ērkun Māntan ebwarīwusis miksjans en Nātangai, prei Pakarwjas kāiman",
     "Прусы с Эркусом Мантасом победили немцы в натангия, под покарвисом деревней"),
]

for cid, pr, exp in cases:
    got = json.loads(tc.translate_pr_sentence_json(pr))["translation"]
    mark = "OK" if got == exp else "FAIL"
    print(f"{mark} {cid}")
    if got != exp:
        print(f"  exp: {exp}")
        print(f"  got: {got}")

# Also check: what does _select_pr_match return for kāiman with original data?
m = tc._select_pr_match('kāiman', prefer_pos=None)
if m:
    print(f'ORIG selected kāiman: id={m[0].get("i")}, w={m[0].get("w")}, label={m[1]}')

m2 = tc._select_pr_match('warewīngi', prefer_pos=None)
if m2:
    print(f'ORIG selected warewīngi: id={m2[0].get("i")}, w={m2[0].get("w")}, label={m2[1]}')
