#!/usr/bin/env python3
import json, sys, re
ROOT = '/media/stan/fleshka/ghsite'
sys.path.insert(0, ROOT)
import translate_core as tc
j = lambda n: open(f'{ROOT}/data/{n}', encoding='utf-8').read()
tc.load_data(j('dictionary.json'), j('overrides.json'), j('phrasebook.json'), j('priorities.json'), j('propernames.json'))

# Monkey-patch to trace
orig_select = tc._select_pr_preposition_sense
def traced_select(prep_clean, next_case, fallback):
    result = orig_select(prep_clean, next_case, fallback)
    if prep_clean == 'pa':
        print(f'_select_pr_preposition_sense("{prep_clean}", next_case={next_case}, fallback={fallback and fallback[0].get("i")}) -> id={result[0].get("i")} ru={result[0].get("ru","")[:40]}')
    return result
tc._select_pr_preposition_sense = traced_select

orig_next_case = tc._next_pr_case
def traced_next_case(tokens, i):
    result = orig_next_case(tokens, i)
    clean = tc._clean_pr_token(tokens[i]) if i < len(tokens) else '?'
    if clean == 'pa':
        print(f'_next_pr_case(tokens, {i}) for "{tokens[i]}" -> {result}')
    return result
tc._next_pr_case = traced_next_case

result = json.loads(tc.translate_pr_sentence_json('pa Teutōtiskas ōrdenas'))
print(f'\nOutput: {result["translation"]}')
