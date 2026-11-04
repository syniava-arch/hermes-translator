#!/usr/bin/env python3
"""Аудит данных переводчика: словарь, оверлеи, имена, фразеологизмы, пробелы."""
import json, re, sys, os
from collections import Counter

ROOT = "/media/stan/fleshka/ghsite"
sys.path.insert(0, ROOT)

def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)

dict_ = load("dictionary.json")
ov = load("overrides.json")
pn = load("propernames.json")
try:
    pb = load("phrasebook.json")
except Exception:
    pb = {}
try:
    pr = load("priorities.json")
except Exception:
    pr = {}

print("=" * 70)
print("АУДИТ ДАННЫХ ПЕРЕВОДЧИКА")
print("=" * 70)

# ---------- 1. СЛОВАРЬ ----------
print("\n### 1. СЛОВАРЬ (dictionary.json)")
print(f"  Всего записей: {len(dict_)}")

no_ru = [e for e in dict_ if not e.get("ru")]
print(f"  Записей БЕЗ ru-глоссы: {len(no_ru)}")

xr = [e for e in dict_ if e.get("x")]
print(f"  Ссылочных записей (x:true): {len(xr)}")
xr_no_target = [e for e in xr if not e.get("b")]
if xr_no_target:
    print(f"    ⚠ x:true без указателя 'b' (битая ссылка): {len(xr_no_target)}")
    for e in xr_no_target[:8]:
        print(f"       id={e.get('i')} w={e.get('w')}")

empty_ru = [e for e in dict_ if e.get("ru") == ""]
if empty_ru:
    print(f"  ⚠ Пустая ru-глосса '': {len(empty_ru)}")
    for e in empty_ru[:8]:
        print(f"       id={e.get('i')} w={e.get('w')}")

# missing i
no_i = [e for e in dict_ if not isinstance(e.get("i"), int)]
if no_i:
    print(f"  ⚠ Записей без целочисленного 'i': {len(no_i)}")

# ---------- 2. ОВЕРЛЕИ ----------
print("\n### 2. ОВЕРЛЕИ (overrides.json)")
print(f"  Всего записей: {len(ov)}")

# placeholders
ph = [e for e in ov if e.get("ru") == e.get("word")]
print(f"  Плейсхолдеры (ru == word, не улучшены): {len(ph)}")
if ph:
    for e in ph[:10]:
        print(f"       {e.get('word')}")
    if len(ph) > 10:
        print(f"       ... ещё {len(ph)-10}")

# missing i (overrides use 'id', not 'i'; check both)
ov_no_id = [e for e in ov if not isinstance(e.get("id"), int)]
if ov_no_id:
    print(f"  ⚠ Записей без целочисленного 'id': {len(ov_no_id)}")
    for e in ov_no_id[:3]:
        print(f"       word={e.get('word')}")

# duplicates by word
wc = Counter(e.get("word", "").lower() for e in ov)
dups = {w: c for w, c in wc.items() if c > 1}
if dups:
    print(f"  ⚠ Дубликаты по word: {len(dups)}")
    for w, c in list(dups.items())[:12]:
        print(f"       {w} ×{c}")

# entries with priority
prio = [e for e in ov if e.get("priority")]
print(f"  Записей с priority: {len(prio)}")

# ---------- 3. СОБСТВЕННЫЕ ИМЕНА ----------
print("\n### 3. ИМЕНА (propernames.json)")
print(f"  Всего: {len(pn)}")
for e in pn:
    print(f"    {e.get('lemma')}: gender={e.get('gender')} ru_sg_nom={e.get('ru',{}).get('sg',{}).get('nom','?')}")

# ---------- 4. ФРАЗЕОЛОГИЗМЫ ----------
print("\n### 4. ФРАЗЕОЛОГИЗМЫ (phrasebook.json)")
if isinstance(pb, dict):
    for k, v in pb.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, list):
                    print(f"  {k}.{kk}: {len(vv)} записей")
                else:
                    print(f"  {k}.{kk}: {vv}")
        elif isinstance(v, list):
            print(f"  {k}: {len(v)} записей")
elif isinstance(pb, list):
    print(f"  Всего записей: {len(pb)}")
else:
    print(f"  Тип: {type(pb).__name__}")

# ---------- 5. ПРИОРИТЕТЫ ----------
print("\n### 5. ПРИОРИТЕТЫ (priorities.json)")
if isinstance(pr, dict):
    for k, v in pr.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for kk, vv in v.items():
                print(f"    {kk}: {vv}")
        else:
            print(f"  {k}: {v}")

# ---------- 6. КЛЮЧЕВЫЕ ПРОБЛЕМНЫЕ ТОКЕНЫ ----------
print("\n### 6. ПРОВЕРКА ИЗВЕСТНЫХ ПРОБЛЕМНЫХ ТОКЕНОВ")
# словарь по заголовкам
by_head = {}
for e in dict_:
    s = e.get("s", [])
    words = s if isinstance(s, list) else [s]
    for w in words:
        if w:
            by_head.setdefault(w.lower(), []).append(e)

for tok in ["sen", "sēn", "prūsai", "paprwarējētan", "walinsnā", "wālinsnā",
            "ebwarīwusis", "audāi", "papeisātan", "miksjans", "raggas"]:
    hits = by_head.get(tok.lower(), [])
    ov_hit = [e for e in ov if e.get("word", "").lower() == tok.lower()]
    status = "в словаре" if hits else "—"
    ru = [e.get("ru") for e in hits[:1]]
    print(f"  {tok:18s}: {status:10s} ru={ru}  override={'есть' if ov_hit else 'нет'}")

print("\n### 7. СЕМАНТИКА 'sen' / 'sēn' (потенциальный конфликт)")
for tok in ["sen", "sēn"]:
    for e in by_head.get(tok.lower(), []):
        print(f"  id={e.get('i')} w={e.get('w')} s={e.get('s')} ru={e.get('ru')}")

print("\n" + "=" * 70)
print("АУДИТ ЗАВЕРШЁН")
print("=" * 70)
