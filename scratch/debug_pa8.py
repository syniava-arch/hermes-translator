#!/usr/bin/env python3
import json, sys
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

# Directly test _ru_gloss_for_entry for id=2233886
entry = None
for e in tc.dictionary:
    if e.get('i') == 2233886:
        entry = e
        break

if entry:
    print(f'Entry: id={entry["i"]} ru={entry["ru"]}')
    
    # Without forced case
    g1, n1 = tc._ru_gloss_for_entry(entry, '')
    print(f'_ru_gloss_for_entry(entry, "") = "{g1}" note="{n1}"')
    
    # With forced_case="datv"
    g2, n2 = tc._ru_gloss_for_entry(entry, '', forced_case='datv')
    print(f'_ru_gloss_for_entry(entry, "", forced_case="datv") = "{g2}" note="{n2}"')
else:
    print('Entry 2233886 not found')

# Check what _select_pr_match('pa') returns vs the sense entry
m = tc._select_pr_match('pa')
print(f'\n_select_pr_match("pa") = id={m[0].get("i")} ru={m[0].get("ru","")}')

# Also check: maybe the fallback (entry,label) from sentence loop is used?
# In _select_pr_preposition_sense, if matching has 1 entry, it returns (matching[0]["entry"], "")
# But then _ru_gloss_for_entry is called with that entry. Let's verify.
result = tc.translate_pr_sentence_json('pa Teutōtiskas')
print(f'\nSentence: "pa Teutōtiskas"')
print(f'Result: {result}')
