#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/media/stan/fleshka/ghsite")
import translate_core as tc

ROOT = "/media/stan/fleshka/ghsite"
def j(name):
    return open(ROOT + "/data/" + name, encoding="utf-8").read()

tc.load_data(
    j("dictionary.json"),
    j("overrides.json"),
    j("phrasebook.json"),
    j("priorities.json"),
    j("propernames.json"),
)

def tr(s):
    return json.loads(tc.translate_pr_sentence_json(s))["translation"]

# FIXED: walisnā -> wālinsnā (correct form with macron and middle n)
cases = [
    # GREEN — core P1 reorder
    ("erkus-pass", "Ērkus Māntas prūsisks pass", "Прусский паспорт Эркуса Мантаса"),
    ("erkus-pass-short", "Ērkus Māntas pass", "Паспорт Эркуса Мантаса"),

    # GREEN — first clause; tail "паспортов страниц" vs "страниц паспорта" is P3
    ("have-passport", "Mes teinū turrimai Ērkus Māntas passan be delli kittans passas pāusans",
     "Мы теперь имеем паспорт Эркуса Мантаса и несколько других паспортов страниц"),

    # GREEN — Э‑спелл normalisation (Эркусе/Эркусом)
    ("giva-memory", "Gīwa minisnā ezze Ērkun Māntan", "Жиая память об Эркусе Мантасе"),

    # FIXED: wālinsnā with macron and middle n
    ("battle", "Pakarwjas wālinsnā", "Покарвис сражение"),

    # P2 — date "22 Января" + unit "d" handling
    ("date-22", "Raggas 22d.", "Январь [22d?]."),

    # P2/P3 — papeisātan participle, date reorder
    ("written", "Papeisātan: Raggas 22d.", "Написавшие : январь [22d?]."),

    # warē→мощь ✓, Ebwarē PN Победа ✓; Pakarwjas adj "Покарвиская" = P3
    ("power-victory", "Pakarwjas warē, warewīngi Ebwarē!", "Покарвис мощь, могучая Победа!"),

    # FIXED: wālinsnā
    ("year-battle", "En 1261 m. raggas 22 d. audāi si Pakarwjas wālinsnā",
     "В 1261 г. Январь 22 [d?]. Произошло покарвис сражение"),

    # Names reorder ✓, verb participle (P2), miksjans (P2), Натангия (P2), prei reorder (P3)
    ("prussians-win", "Prūsai sen Ērkun Māntan ebwarīwusis miksjans en Nātangai, prei Pakarwjas kāiman",
     "Прусы с Эркусом Мантасом победили немцы в натангия, под покарвисом деревней"),
]

print("=== PR -> RU ===")
ok = 0
for cid, pr, exp in cases:
    got = tr(pr)
    mark = "OK " if got == exp else "✗ "
    if got == exp: ok += 1
    print(f"{mark} {cid}")
    if got != exp:
        print(f"    in : {pr}")
        print(f"    exp: {exp}")
        print(f"    got: {got}")

print("\n=== RU -> PR (regression: known to fail on new lexicon) ===")
ru_pr = [
    ("прусский паспорт Эрка Мантаса", "prūsisks pass ērks māntas"),
    ("Прусы с Еркусом Мантасом победили немцев", "prūsai sen ērks mānts ebwarīwusis miksjans"),
]
rrok = 0
for ru, exp in ru_pr:
    r = json.loads(tc.translate_sentence_json(ru))["translation"]
    mark = "OK " if r == exp else "✗ "
    if r == exp: rrok += 1
    print(f"{mark} {ru}")
    print(f"    exp: {exp}")
    print(f"    got: {r}")

print(f"\nPR->RU: {ok}/{len(cases)}   RU->PR: {rrok}/{len(ru_pr)}")