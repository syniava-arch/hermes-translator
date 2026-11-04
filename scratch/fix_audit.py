#!/usr/bin/env python3
"""Исправляет ошибки аудита:
1. 2180 оверлеев без id: присваивает id по совпадению word -> dictionary[].w
   (оставшиеся без совпадения — orphan ru, добавляем в словарь)
2. 12 дубликатов оверлеев: оставляем запись с id, удаляем дубликат без id
3. 52 записи словаря с пустым ru: большинство — cross-ref заглушки (↑ в s),
   оставшиеся — заполняем переводом из overrides или пометкой.
4. 1 битая cross-ref interwju (id=9418, x:true без b): убираем x:true.
"""
import json, re, sys, os
from collections import Counter

ROOT = "/media/stan/fleshka/ghsite"
sys.path.insert(0, ROOT)

d = json.load(open(f"{ROOT}/data/dictionary.json", encoding="utf-8"))
ov = json.load(open(f"{ROOT}/data/overrides.json", encoding="utf-8"))

# ---------- 1. Build dict lookup by headword ----------
by_head = {}
for e in d:
    w = (e.get("w") or "").lower()
    by_head.setdefault(w, []).append(e)

# ---------- 2. Fix overrides without id ----------
ov_fixed = []
orphan_added = 0
orphan_skipped = 0
dups_removed = 0

for o in ov:
    if isinstance(o.get("id"), int):
        ov_fixed.append(o)
        continue

    # Try to match to dictionary entry by word
    word_lower = (o.get("word") or "").lower()
    matches = by_head.get(word_lower, [])
    if len(matches) == 1:
        o["id"] = matches[0]["i"]
        ov_fixed.append(o)
    elif len(matches) > 1:
        # Multiple matches — ambiguous, skip (would need manual review)
        orphan_skipped += 1
    else:
        # No dictionary match — orphan translation
        # Add as a new dictionary entry
        # Skip the synthetic "new-m-unit" entry (string id)
        int_ids = [e.get("i") for e in d if isinstance(e.get("i"), int)]
        new_id = max(int_ids) + 1 + orphan_added
        new_entry = {
            "i": new_id,
            "w": o.get("word", ""),
            "l": (o.get("word", "")[0] if o.get("word") else "").upper(),
            "s": "",
            "x": False,
            "b": "",
            "g": "",
            "ru": o.get("ru", ""),
            "lt": o.get("lt", ""),
            "lv": o.get("lv", ""),
            "de": o.get("de", ""),
            "en": o.get("en", ""),
            "pl": o.get("pl", ""),
        }
        d.append(new_entry)
        o["id"] = new_id
        ov_fixed.append(o)
        orphan_added += 1

print(f"1. Overrides: assigned id to {len(ov) - len([o for o in ov if not isinstance(o.get('id'), int)]) - orphan_skipped} entries")
print(f"   Orphans added to dictionary: {orphan_added}")
print(f"   Orphans skipped (ambiguous): {orphan_skipped}")

# ---------- 3. Deduplicate by word, keep entry with id ----------
# Group by word (case-insensitive)
by_word = {}
for o in ov_fixed:
    key = (o.get("word") or "").lower()
    by_word.setdefault(key, []).append(o)

ov_deduped = []
removed = 0
for key, entries in by_word.items():
    if len(entries) == 1:
        ov_deduped.append(entries[0])
    else:
        # Keep entry with id, prefer higher id (more specific)
        with_id = [e for e in entries if isinstance(e.get("id"), int)]
        if with_id:
            best = max(with_id, key=lambda e: e.get("id", 0))
            ov_deduped.append(best)
            removed += len(entries) - 1
        else:
            # All without id — keep first
            ov_deduped.append(entries[0])
            removed += len(entries) - 1

print(f"2. Deduped: removed {removed} duplicate entries")

# ---------- 4. Fix 52 empty-ru dictionary entries ----------
empty_ru = [e for e in d if not e.get("ru")]
print(f"3. Dictionary entries with empty ru: {len(empty_ru)}")

# Rebuild by_head after potential additions
by_head = {e.get("w","").lower(): e for e in d}

fixed_ru = 0
for e in empty_ru:
    s = e.get("s", "")
    # Check if it's a cross-ref (informal ↑ or formal x:true)
    is_xref = e.get("x") or "↑" in str(s)

    if is_xref:
        # Cross-ref: check if target exists
        # Extract target from ↑ field
        m = re.search(r'↑\s*(\S+)', str(s))
        if m:
            target = m.group(1).lower()
            target_entry = by_head.get(target)
            if target_entry:
                e["ru"] = target_entry.get("ru", "")
                fixed_ru += 1
            else:
                e["ru"] = f"[→{target}?]"
        else:
            # Formal cross-ref with x:true but no 'b'
            if e.get("x") and not e.get("b"):
                e["x"] = False
                e["ru"] = "[xref]"
                fixed_ru += 1
            else:
                e["ru"] = "[пусто]"
    else:
        # Not a cross-ref — try to find override
        word_lower = (e.get("w") or "").lower()
        ov_match = [o for o in ov_deduped if (o.get("word") or "").lower() == word_lower]
        if ov_match:
            e["ru"] = ov_match[0].get("ru", "")
            fixed_ru += 1
        else:
            e["ru"] = "[пусто]"

print(f"   Fixed (filled or marked): {fixed_ru}")
print(f"   Still empty: {len([e for e in d if not e.get('ru')])}")

# ---------- 5. Fix broken cross-ref interwju ----------
for e in d:
    if e.get("i") == 9418:
        if e.get("x") and not e.get("b"):
            e["x"] = False
            print(f"4. Fixed cross-ref id=9418 (interwju): x:true → False")

# ---------- Save ----------
with open(f"{ROOT}/data/dictionary.json", "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, separators=(",", ":"))
    f.flush()
    os.fsync(f.fileno())

with open(f"{ROOT}/data/overrides.json", "w", encoding="utf-8") as f:
    json.dump(ov_deduped, f, ensure_ascii=False, separators=(",", ":"))
    f.flush()
    os.fsync(f.fileno())

print(f"\nSaved:")
print(f"  dictionary.json: {len(d)} entries")
print(f"  overrides.json: {len(ov_deduped)} entries")

# Summary of remaining issues
empty = [e for e in d if not e.get("ru")]
if empty:
    print(f"\n⚠ Still {len(empty)} entries with empty ru:")
    for e in empty:
        print(f"  id={e.get('i')} w={e.get('w')} s={e.get('s')}")
