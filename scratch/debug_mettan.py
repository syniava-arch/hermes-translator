#!/usr/bin/env python3
import json, sys, re
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

# Monkey-patch _ru_gloss_for_entry to trace mettan
orig_ru_gloss = tc._ru_gloss_for_entry
def traced_ru_gloss(entry, label, forced_case=None, agreement=None, subject_gender=None, subject_number=None, num_government=False):
    w = (entry.get("w") or "").lower()
    if w == "mettan":
        print(f'_ru_gloss_for_entry(mettan, label={label!r}, forced_case={forced_case!r}, num_government={num_government})')
    result = orig_ru_gloss(entry, label, forced_case, agreement, subject_gender, subject_number, num_government)
    if w == "mettan":
        print(f'  -> {result}')
    return result
tc._ru_gloss_for_entry = traced_ru_gloss

# Also trace PREP handling for 'en'
orig_select_prep = tc._select_pr_preposition_sense
def traced_select_prep(prep_clean, next_case, fallback):
    if prep_clean == 'en':
        result = orig_select_prep(prep_clean, next_case, fallback)
        print(f'_select_pr_preposition_sense("en", next_case={next_case}) -> id={result[0].get("i")} ru={result[0].get("ru","")[:20]}')
        return result
    return orig_select_prep(prep_clean, next_case, fallback)
tc._select_pr_preposition_sense = traced_select_prep

result = tc.translate_pr_sentence_json('en 1273 mettan')
print(f'\nResult: {result}')
