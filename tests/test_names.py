"""Имена и локатив: что должно получаться в обе стороны.

Проверяет три вещи:
  1) русские имена из data/propernames.json узнаются и получают нужный падеж;
  2) «в + место» даёт форму места (en + датив/локатив), а «в + направление» —
     винительный;
  3) прусские имена в тексте возвращаются по-русски.

Запуск из корня репозитория:
    python3 tests/test_names.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import translate_core as tc  # noqa: E402


def read(name):
    return open(os.path.join(ROOT, "data", name), encoding="utf-8").read()


tc.load_data(
    read("dictionary.json"),
    read("overrides.json"),
    read("phrasebook.json"),
    read("priorities.json"),
    read("propernames.json"),
)


def ru_to_pr(sentence):
    return json.loads(tc.translate_sentence_json(sentence))["translation"].strip()


def pr_to_ru(sentence):
    return json.loads(tc.translate_pr_sentence_json(sentence))["translation"].strip()


# (русская фраза, что должно быть в переводе, пояснение)
RU_CASES = [
    ("Эркс живёт в Литве", "Ērks", "имя в именительном"),
    ("Я вижу Мантаса", "Māntan", "имя в винительном"),
    ("Я вижу Абдангу", "Abdāngan", "сгенерированное имя, женское -a, винительный"),
    ("Абданга живёт в Литве", "Abdānga", "сгенерированное имя, именительный"),
]

PLACES = [
    ("Мы в Пруссии", "en Prūsijai", "место: en + форма места"),
    ("Дом в лесу", "en meddju", "место: en + форма места"),
    ("Он идёт в город", "en mēstan", "направление: en + винительный"),
    ("Брат идёт в лес", "en meddjan", "направление: en + винительный"),
]

PR_TO_RU = [
    ("Ērks ast mans brāti", "Эркс", "имя из курируемой записи"),
    ("Abdāngan as wīda", "Абдангса", "сгенерированное имя в винительном"),
]

failures = []

for phrase, expected, why in RU_CASES + PLACES:
    got = ru_to_pr(phrase)
    if expected.lower() not in got.lower():
        failures.append(f"RU→PR «{phrase}» ({why}): ждали «{expected}», получили «{got}»")

for phrase, expected, why in PR_TO_RU:
    got = pr_to_ru(phrase)
    if expected.lower() not in got.lower():
        failures.append(f"PR→RU «{phrase}» ({why}): ждали «{expected}», получили «{got}»")

# Сгенерированный файл не должен разъезжаться с генератором.
names = json.loads(read("propernames.json"))
curated = json.loads(read("propernames-curated.json"))
by_lemma = {e["lemma"]: e for e in names}
if len(names) < 2000:
    failures.append(f"propernames.json: {len(names)} записей, ждали ~2 100")
for entry in curated:
    got = by_lemma.get(entry["lemma"])
    if got is None:
        failures.append(f"курируемое имя {entry['lemma']} пропало из propernames.json")
    elif got["ru"]["sg"] != entry["ru"]["sg"]:
        failures.append(f"курируемое имя {entry['lemma']} перезаписано генератором")

print(f"проверок имён и места: {len(RU_CASES) + len(PLACES) + len(PR_TO_RU)}, "
      f"записей в propernames.json: {len(names)}")
print(f"провалов: {len(failures)}")
for line in failures:
    print("  -", line)
sys.exit(1 if failures else 0)
