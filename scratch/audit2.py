#!/usr/bin/env python3
"""Аудит оверлеев: who has id, who doesn't, duplicates."""
import json, sys
from collections import Counter

ROOT = "/media/stan/fleshka/ghsite"
ov = json.load(open(f"{ROOT}/data/overrides.json", encoding="utf-8"))

with_id = [e for e in ov if isinstance(e.get("id"), int)]
without_id = [e for e in ov if not isinstance(e.get("id"), int)]
print(f"overrides: {len(ov)}")
print(f"  with id: {len(with_id)}")
print(f"  without id: {len(without_id)}")

w_paradigm = [e for e in without_id if "paradigm" in e]
w_ru_only = [e for e in without_id if "ru" in e and "paradigm" not in e]
w_other = [e for e in without_id if "paradigm" not in e and "ru" not in e]
print(f"  dead (word+ru, no paradigm): {len(w_ru_only)}")
print(f"  dead (word+paradigm): {len(w_paradigm)}")
print(f"  other (no ru, no paradigm): {len(w_other)}")

print("\n=== Sample dead entries (word+ru only) ===")
for e in w_ru_only[:8]:
    print(f"  {e.get('word')}: {e.get('ru')}")
print("  ...")

# Check duplicates
wc = Counter(e.get("word","").lower() for e in ov)
dups = {w: c for w, c in wc.items() if c > 1}
print(f"\nDuplicates (12 words):")
for w, c in dups.items():
    entries = [e for e in ov if e.get("word","").lower() == w]
    ids = [e.get("id") for e in entries]
    print(f"  {w} x{c}: ids={ids}")

# 52 empty-ru entries
print("\n=== 52 empty-ru dictionary entries ===")
d = json.load(open(f"{ROOT}/data/dictionary.json", encoding="utf-8"))
empty = [e for e in d if not e.get("ru")]
for e in empty:
    print(f"  id={e.get('i')} w={e.get('w')} s={e.get('s')}")

# broken cross-ref
xr = [e for e in d if e.get("x") and not e.get("b")]
print(f"\nBroken cross-refs (x:true, no 'b'): {len(xr)}")
for e in xr:
    print(f"  id={e.get('i')} w={e.get('w')}")
