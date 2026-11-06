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

# Test individual words
test_words = ["turrimai", "as", "Mes", "teinū"]
for word in test_words:
    print(f"\nTesting word: '{word}'")
    try:
        result = translate_core.translate_pr_sentence_json(word)
        print(f"Translation: {result}")
    except Exception as e:
        print(f"Error: {e}")

# Test phrases
test_phrases = [
    "Mes teinū",
    "Prūsai sen Ērks Mānts ebwarīwusis miksjans en Nātangai",
    "Papeisātan: Raggas 22d."
]

for phrase in test_phrases:
    print(f"\nTesting phrase: '{phrase}'")
    try:
        result = translate_core.translate_pr_sentence_json(phrase)
        print(f"Translation: {result}")
    except Exception as e:
        print(f"Error: {e}")

# Test verb conjugation with subject agreement
print(f"\nTesting verb conjugation with subject agreement:")
test_verbs = [
    ("turrimai", "мы"),
    ("turītun", "иметь"),
    ("as tū", "я ты"),
    ("mes teinū turrimai", "мы теперь иметь")
]

for prussian, russian_hint in test_verbs:
    print(f"Testing: '{prussian}' (hint: {russian_hint})")
    try:
        result = translate_core.translate_pr_sentence_json(prussian)
        print(f"Translation: {result}")
    except Exception as e:
        print(f"Error: {e}")