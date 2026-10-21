#!/usr/bin/env python3
# v2 data wiring: preposition/lexicon fixes + new entries + PN forms.
import json, io, re
ROOT = "/media/stan/fleshka/ghsite"

# ---- 1. dictionary.json: turn `sen` (id 5535, "себя") into prep "с" ----
dp = ROOT + "/data/dictionary.json"
txt = open(dp, encoding="utf-8").read()
old = ('    "s": "\u2191 Sin [sien 49(1)]",\n'
       '    "de": "",\n'
       '    "en": "",\n'
       '    "lt": "",\n'
       '    "lv": "",\n'
       '    "pl": "",\n'
       '    "ru": "\u0441\u0435\u0431\u044f"\n')
new = ('    "s": "prp acc [sen 49(1)]",\n'
       '    "de": "",\n'
       '    "en": "",\n'
       '    "lt": "",\n'
       '    "lv": "",\n'
       '    "pl": "",\n'
       '    "ru": "\u0441"\n')
assert txt.count(old) == 1, f"sen entry unique match = {txt.count(old)}"
txt = txt.replace(old, new)
open(dp, "w", encoding="utf-8").write(txt)
print("patched dictionary: sen -> с (prep acc)")

# ---- 2. overrides.json: append fresh entries (non-headword new words) ----
op = ROOT + "/data/overrides.json"
ov_txt = open(op, encoding="utf-8").read()
anchor = ('        "akk": "M\u012bngans"\n'
          '        }\n'
          '      }\n'
          '    }\n'
          '  }\n'
          ']')
assert ov_txt.count(anchor) == 1, f"overrides tail match = {ov_txt.count(anchor)}"
fresh = [
    {"word": "prei", "source": "prp acc", "ru": "под", "priority": 1},
    {"word": "Prūsai", "source": "n pl nom", "ru": "Прусы", "priority": 1},
    {"word": "minisnā", "source": "n sg nom", "ru": "память", "priority": 1},
    {"word": "walisnā", "source": "n sg nom", "ru": "сражение", "priority": 1},
    {"word": "warewīngi", "source": "aj nom", "ru": "могучая", "priority": 1},
    {"word": "raggas", "source": "n sg nom", "ru": "Январь", "priority": 1},
    {"word": "kāiman", "source": "n sg acc", "ru": "деревня", "priority": 1},
    {"word": "miksjans", "source": "n pl gen", "ru": "немцев", "priority": 1},
    {"word": "ebwarīwusis", "source": "v pt past", "ru": "победили", "priority": 1},
    {"word": "Nātangai", "source": "n sg loc", "ru": "Натангия", "priority": 1},
    {"word": "Ebwarē", "source": "n fem nom", "ru": "Победа", "priority": 1},
    {"word": "Papeisātan", "source": "v pa", "ru": "написана", "priority": 1},
    {"word": "Pakarwjas", "source": "n sg nom", "ru": "Покарвис", "priority": 1},
]
entry_texts = []
for e in fresh:
    entry_texts.append("  " + json.dumps(e, ensure_ascii=False))
new_block = anchor.replace(
    '  }\n]',
    '  },\n' + ",\n".join(entry_texts) + "\n]"
)
ov_txt = ov_txt.replace(anchor, new_block)
open(op, "w", encoding="utf-8").write(ov_txt)
print("appended", len(fresh), "fresh override entries")

# ---- 3. propernames.json: add Gīwa + ērks alias Ērkun ----
pp = ROOT + "/data/propernames.json"
pn = json.load(open(pp, encoding="utf-8"))
for e in pn:
    if e.get("lemma") == "Ērks":
        al = e.setdefault("aliases", [])
        if "Ērkun" not in al:
            al.append("Ērkun")
pn.append({
    "lemma": "Gīwa",
    "aliases": [],
    "gender": "fem",
    "priority": 1,
    "pr": {"sg": {"nom": "Gīwa", "gen": "Gīwas", "dat": "Gīwai", "akk": "Gīwam", "ins": "Gīwu", "prl": "Gīwā"}},
    "ru": {"sg": {"nom": "Жиая", "gen": "Жиаи", "dat": "Жиае", "acc": "Жиаю", "ins": "Жиа", "prl": "Жиа"}}
})
json.dump(pn, open(pp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("propernames: added Gīwa + ērks alias Ērkun")

# ---- 4. priorities.json: pa -> по (disambiguate 3-sense pa) ----
pjp = ROOT + "/data/priorities.json"
pr = json.load(open(pjp, encoding="utf-8"))
pr.setdefault("pr_to_ru", {})
pr["pr_to_ru"]["pa"] = "по"
json.dump(pr, open(pjp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("priorities: pa -> по")
print("DONE")
