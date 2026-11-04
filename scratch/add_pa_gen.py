#!/usr/bin/env python3
"""Add dictionary entry for pa + genitive -> согласно."""
import json, sys, os

ROOT = '/media/stan/fleshka/ghsite'
d = json.load(open(f'{ROOT}/data/dictionary.json', encoding='utf-8'))

# Find the max id (skip non-integer ids)
int_ids = [e.get('i', 0) for e in d if isinstance(e.get('i'), int)]
max_id = max(int_ids)

# Add new entry for pa + genitive
new_entry = {
    "i": max_id + 1,
    "w": "pa",
    "l": "P",
    "f": "",
    "x": False,
    "b": "",
    "g": "prp gent",
    "s": "prp gent [po 99]",
    "de": "gemäß",
    "en": "according to",
    "lt": "pagal",
    "lv": "pēc",
    "pl": "według",
    "ru": "согласно",
}
d.append(new_entry)

with open(f'{ROOT}/data/dictionary.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, separators=(',',':'))
    f.flush()
    os.fsync(f.fileno())

print(f'Added pa + genitive entry: id={new_entry["i"]}, ru={new_entry["ru"]}, s={new_entry["s"]}')
print(f'Total dictionary entries: {len(d)}')
