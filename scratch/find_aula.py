#!/usr/bin/env python3
import json
d = json.load(open('/media/stan/fleshka/ghsite/data/dictionary.json', encoding='utf-8'))
for e in d:
    if 'aula' in (e.get('w') or '').lower():
        print(json.dumps(e, ensure_ascii=False))
