"""Golden-набор переводчика: фразы, которые обязаны работать.

У кейса три состояния:
  required    — провал = красный тест (регресс);
  known-weak  — известно, что пока плохо; провал не считается, но если кейс
                НАЧАЛ проходить, тест об этом громко пишет: перенеси в required;
  ratio       — метрика без эталона (доля форм override), сравнивается с
                baseline из файла, падение = провал.

Запуск из корня репозитория:
    python3 tests/test_golden.py
    python3 tests/test_golden.py --verbose
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import translate_core as tc  # noqa: E402

GOLDEN = os.path.join(ROOT, "tests", "golden.json")


def read(name):
    return open(os.path.join(ROOT, "data", name), encoding="utf-8").read()


def norm(text):
    """Сравнение без нервов: регистр, лишние пробелы и точки в сокращениях."""
    text = (text or "").replace("ё", "е")
    text = re.sub(r"\s+", " ", text).strip().lower()
    text = re.sub(r"\s*([.,!?;:])\s*", r"\1", text)
    return text


tc.load_data(
    read("dictionary.json"),
    read("overrides.json"),
    read("phrasebook.json"),
    read("priorities.json"),
    read("propernames.json"),
)


def translate(case):
    text = case["in"]
    if case.get("dir", "ru->pr") == "pr->ru":
        return json.loads(tc.translate_pr_sentence_json(text))["translation"]
    return json.loads(tc.translate_sentence_json(text))["translation"]


def matched(case, got):
    mode = case.get("mode", "exact")
    if mode == "contains":
        return norm(case["expect"]) in norm(got)
    return norm(case["expect"]) == norm(got)


def main():
    verbose = "--verbose" in sys.argv
    data = json.load(open(GOLDEN, encoding="utf-8"))
    cases = data.get("cases", [])

    failed, improved, passed = [], [], 0
    rows = []
    for case in cases:
        got = translate(case)
        ok = matched(case, got)
        status = case.get("status", "required")
        if ok:
            passed += 1
            if status == "known-weak":
                improved.append((case["id"], got))
        else:
            if status == "required":
                failed.append((case, got))
        rows.append((case["id"], status, ok, got))

    ratio_failed = []
    for metric in data.get("ratios", []):
        current = metric.get("current")
        baseline = metric.get("baseline")
        if current is None or baseline is None:
            continue
        if current < baseline - 1e-9:
            ratio_failed.append((metric["name"], baseline, current))

    width = max((len(r[0]) for r in rows), default=6)
    print(f"{'кейс'.ljust(width)}  статус       результат")
    for cid, status, ok, got in rows:
        mark = "ok" if ok else ("ПРОВАЛ" if status == "required" else "известно")
        print(f"{cid.ljust(width)}  {status.ljust(12)} {mark}")
        if verbose and not ok:
            print(f"{'':{width}}    ждали: {next(c['expect'] for c in cases if c['id'] == cid)}")
            print(f"{'':{width}}    вышло: {got}")

    weak = sum(1 for c in cases if c.get("status") == "known-weak")
    print()
    print(f"кейсов: {len(cases)} | прошло: {passed} | required: {len(cases) - weak} "
          f"| known-weak: {weak} | провалов: {len(failed)}")

    for cid, got in improved:
        print(f"  ! «{cid}» начал проходить: {got}")
        print("    перенеси в required (status), иначе улучшение не закреплено")

    for name, baseline, current in ratio_failed:
        print(f"  ! метрика «{name}» упала: было {baseline}, стало {current}")

    for case, got in failed:
        print(f"  - провал «{case['id']}»")
        print(f"    ждали: {case['expect']}")
        print(f"    вышло: {got}")

    sys.exit(1 if failed or ratio_failed else 0)


if __name__ == "__main__":
    main()
