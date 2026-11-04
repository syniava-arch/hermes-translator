#!/usr/bin/env python3
import json
d = json.load(open('/media/stan/fleshka/ghsite/data/dictionary.json', encoding='utf-8'))
types = {}
for e in d:
    t = type(e.get('i')).__name__
    types[t] = types.get(t, 0) + 1
print('i field types:', types)
str_ids = [e.get('i') for e in d if isinstance(e.get('i'), str)]
print('string ids sample:', str_ids[:10])
