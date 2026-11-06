#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import translate_core
import json

# Load the data files first
print("Loading data files...")

with open('data/dictionary.json', 'r', encoding='utf-8') as f:
    dictionary_json = f.read()

with open('data/overrides.json', 'r', encoding='utf-8') as f:
    overrides_json = f.read()

with open('data/phrasebook.json', 'r', encoding='utf-8') as f:
    phrasebook_json = f.read()

with open('data/priorities.json', 'r', encoding='utf-8') as f:
    priorities_json = f.read()

with open('data/propernames.json', 'r', encoding='utf-8') as f:
    propernames_json = f.read()

# Load the data
translate_core.load_data(
    dictionary_json, 
    overrides_json, 
    phrasebook_json, 
    priorities_json, 
    propernames_json
)

print("Data loaded successfully!")

# Test the translation of "turrimai"
test_word = "turrimai"
print(f"\nTesting translation of: {test_word}")

# Try to translate from Prussian to Russian
try:
    result = translate_core.translate_pr_sentence_json(test_word)
    print(f"Translation result: {result}")
except Exception as e:
    print(f"Error during translation: {e}")

# Test with a known working word
test_word2 = "as"
print(f"\nTesting translation of: {test_word2}")
try:
    result2 = translate_core.translate_pr_sentence_json(test_word2)
    print(f"Translation result: {result2}")
except Exception as e:
    print(f"Error during translation: {e}")

# Test with a simple phrase
test_phrase = "Mes teinū"
print(f"\nTesting translation of: {test_phrase}")
try:
    result3 = translate_core.translate_pr_sentence_json(test_phrase)
    print(f"Translation result: {result3}")
except Exception as e:
    print(f"Error during translation: {e}")