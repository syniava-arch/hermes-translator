#!/usr/bin/env python3
"""Fix pa + genitive entry: s field should use 'gen' not 'gent'."""
import json, sys, os

ROOT = '/media/stan/fleshka/ghsite'
d = json.load(open(f'{ROOT}/data/dictionary.json', encoding='utf-8'))

# Find and fix the pa genitive entry (last one added)
for e in d:
    if e.get('i') == 2233886:
        old_s = e.get('s', '')
        e['s'] = 'prp gen [po 99]'
        print(f'Fixed id=2233886: s="{old_s}" -> "{e["s"]}"')
        break

with open(f'{ROOT}/data/dictionary.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, separators=(',',':'))
    f.flush()
    os.fsync(f.fileno())

# Verify
d2 = json.load(open(f'{ROOT}/data/dictionary.json', encoding='utf-8'))
for e in d2:
    if e.get('i') == 2233886:
        print(f'Verified: id={e["i"]} s={e["s"]} ru={e["ru"]}')
