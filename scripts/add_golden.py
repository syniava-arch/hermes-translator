"""Добавить кейс в golden-набор из тройки «вход → вышло → как должно».

Пример:
    python3 scripts/add_golden.py --dir ru->pr \
        --in "Прусский паспорт Эркуса Мантаса" \
        --want "Ērkus Māntas prūsisks pass" \
        --source "пользователь, 2026-11-03"

Скрипт сам прогоняет фразу через движок и ставит статус:
  required    — если текущий вывод уже совпадает с «как должно»;
  known-weak  — если ещё нет (тогда тест зелёный, но считает долг).
Идентификатор — транслит из --id или латинский слаг из фразы.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import translate_core as tc  # noqa: E402

GOLDEN = os.path.join(ROOT, "tests", "golden.json")

SLUG = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh',
    'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c',
    'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
    'я': 'ya',
}


def slug(text):
    out = []
    for ch in text.lower():
        if ch in SLUG:
            out.append(SLUG[ch])
        elif ch.isalnum() and ch.isascii():
            out.append(ch)
        else:
            out.append('-')
    return re.sub(r'-+', '-', ''.join(out)).strip('-')[:40]


def read(name):
    return open(os.path.join(ROOT, "data", name), encoding="utf-8").read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="ru->pr", choices=["ru->pr", "pr->ru"])
    ap.add_argument("--in", dest="source_text", required=True)
    ap.add_argument("--want", required=True)
    ap.add_argument("--id")
    ap.add_argument("--mode", default="exact", choices=["exact", "contains"])
    ap.add_argument("--source", default="пользователь")
    args = ap.parse_args()

    tc.load_data(
        read("dictionary.json"),
        read("overrides.json"),
        read("phrasebook.json"),
        read("priorities.json"),
        read("propernames.json"),
    )

    if args.dir == "pr->ru":
        got = json.loads(tc.translate_pr_sentence_json(args.source_text))["translation"]
    else:
        got = json.loads(tc.translate_sentence_json(args.source_text))["translation"]

    def norm(t):
        t = re.sub(r"\s+", " ", (t or "").replace("ё", "е")).strip().lower()
        return re.sub(r"\s*([.,!?;:])\s*", r"\1", t)

    ok = norm(args.want) in norm(got) if args.mode == "contains" else norm(args.want) == norm(got)

    data = json.load(open(GOLDEN, encoding="utf-8"))
    cid = args.id or slug(args.source_text)
    if any(c["id"] == cid for c in data["cases"]):
        print(f"кейс «{cid}» уже есть в наборе — ничего не добавлено")
        return 1

    data["cases"].append({
        "id": cid,
        "dir": args.dir,
        "in": args.source_text,
        "expect": args.want,
        "mode": args.mode,
        "status": "required" if ok else "known-weak",
        "source": args.source,
    })
    json.dump(data, open(GOLDEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"добавлен «{cid}» со статусом {'required' if ok else 'known-weak'}")
    print(f"  ждали: {args.want}")
    print(f"  вышло: {got}")
    if not ok:
        print("  пока не проходит — тест зелёный, но кейс остаётся в долге")
    return 0


if __name__ == "__main__":
    sys.exit(main())
