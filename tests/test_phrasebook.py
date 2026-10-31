"""Регресс по корпусу phrasebook.json.

Проверяет, что каждая готовая пара находится в ОБОИХ направлениях и
возвращает ровно свой перевод/оригинал, а не пословную сборку.

Запуск из корня репозитория:
    python3 tests/test_phrasebook.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import translate_core as tc  # noqa: E402


def read(name):
    return open(os.path.join(ROOT, "data", name), encoding="utf-8").read()


stats = tc.load_data(
    read("dictionary.json"),
    read("overrides.json"),
    read("phrasebook.json"),
    read("priorities.json"),
    read("propernames.json"),
)
print("словарь:", stats)

items = json.loads(read("phrasebook.json"))

pairs = []
for item in items:
    pr = item.get("pr")
    if isinstance(pr, list):
        pr = pr[0] if pr else ""
    ru = item.get("ru_out") or (item.get("ru") or [None])[0]
    if isinstance(ru, list):
        ru = ru[0] if ru else ""
    if pr and ru:
        pairs.append((str(pr), str(ru)))

fail = []
for pr, ru in pairs:
    got = json.loads(tc.translate_pr_sentence_json(pr))["translation"].strip()
    if got != ru.strip():
        fail.append(("PR->RU", pr, ru, got))

    got_back = json.loads(tc.translate_sentence_json(ru))["translation"].strip()
    expected_pr = pr.strip().rstrip(".!?")
    if got_back.rstrip(".!?").strip() != expected_pr.rstrip(".!?"):
        fail.append(("RU->PR", ru, pr, got_back))

print(f"\nпар в фразбуке: {len(pairs)}")
print(f"провалов: {len(fail)}")
for direction, src, exp, got in fail[:20]:
    print(f"\n[{direction}] {src}\n  ждали: {exp}\n  вышло: {got}")


# --- несколько предложений одним вводом -------------------------------------
# Фраза корпуса не должна «ломаться» о запятую внутри себя, а склейка двух
# реплик должна давать склейку их переводов, а не пословную кашу.
multi_fail = []
for (pr1, ru1), (pr2, ru2) in zip(pairs, pairs[1:]):
    got = json.loads(tc.translate_pr_sentence_json(f"{pr1} {pr2}"))["translation"].strip()
    want = f"{ru1.strip()} {ru2.strip()}"

    def canon(x):
        x = re.sub(r"[^\w\s-]", " ", x.lower().replace("—", " "))
        return " ".join(x.split())

    if canon(got) != canon(want):
        multi_fail.append((f"{pr1} {pr2}", want, got))

print(f"\nсклеек по два предложения: {len(pairs) - 1}")
print(f"провалов: {len(multi_fail)}")
for src, exp, got in multi_fail[:10]:
    print(f"\n[2 предложения] {src}\n  ждали: {exp}\n  вышло: {got}")

fail.extend(multi_fail)

sys.exit(1 if fail else 0)
