#!/usr/bin/env python3
import pymorphy3
morph = pymorphy3.MorphAnalyzer()
p = morph.parse("тевтонский")[0]
for case in ["nomn", "gent", "datv", "accs", "ablt", "loct"]:
    try:
        inf = p.inflect({case})
        if inf:
            print(f"{case}: {inf.word}")
    except Exception as e:
        print(f"{case}: ERROR {e}")
