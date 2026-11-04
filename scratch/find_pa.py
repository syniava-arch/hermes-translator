#!/usr/bin/env python3
import json
d = json.load(open('/media/stan/fleshka/ghsite/data/dictionary.json', encoding='utf-8'))
for e in d:
    if (e.get('w') or '').lower() == 'pa':
        print(json.dumps(e, ensure_ascii=False, indent=2))

# Check overrides for pa
ov = json.load(open('/media/stan/fleshka/ghsite/data/overrides.json', encoding='utf-8'))
for o in ov:
    if (o.get('word') or '').lower() == 'pa':
        print('override:', json.dumps(o, ensure_ascii=False, indent=2))
