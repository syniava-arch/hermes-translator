"""Сборка data/propernames.json: русские имена и их прусские падежи.

Запуск из корня репозитория:
    python3 scripts/build_propernames.py

Курируемые вручную записи лежат в data/propernames-curated.json и всегда
перекрывают сгенерированные. Из dictionary.json берутся статьи с глоссом
«прусское мужское/женское имя» — их около 2 100.
"""
import json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data') + os.sep

TR = {
    'ā': 'а', 'â': 'а', 'à': 'а', 'á': 'а', 'a': 'а',
    'ē': 'е', 'ê': 'е', 'è': 'е', 'é': 'е', 'e': 'е',
    'ī': 'и', 'î': 'и', 'ì': 'и', 'í': 'и', 'i': 'и', 'y': 'и',
    'ō': 'о', 'ô': 'о', 'ò': 'о', 'ó': 'о', 'o': 'о',
    'ū': 'у', 'û': 'у', 'ù': 'у', 'ú': 'у', 'u': 'у',
    'b': 'б', 'c': 'ц', 'č': 'ч', 'd': 'д', 'f': 'ф', 'g': 'г',
    'h': 'х', 'j': 'й', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н',
    'p': 'п', 'q': 'к', 'r': 'р', 's': 'с', 'š': 'ш', 't': 'т',
    'v': 'в', 'w': 'в', 'z': 'з', 'ž': 'ж',
}
MULTI = {'ai': 'ай', 'ei': 'ей', 'au': 'ау', 'ui': 'уй'}


def translit(word):
    low = word.lower()
    out, i = [], 0
    while i < len(low):
        two = low[i:i + 2]
        if two in MULTI:
            out.append(MULTI[two])
            i += 2
            continue
        out.append(TR.get(low[i], low[i]))
        i += 1
    res = ''.join(out)
    if word[:1] in 'Ēē' and res.startswith('е'):
        res = 'э' + res[1:]
    res = res[:1].upper() + res[1:]
    return re.sub(r'([бвгджзклмнпрстфхцчшщ])\1', r'\1', res)


def pr_block(lemma, gender):
    """Прусские падежи по шаблону, снятому с парадигм обычных существительных.

    -s (муж.):  gen -as,  dat -u,   akk -an      (Ādams, mēstas)
    -is (муж.): gen -jas, dat -ju,  akk -jan     (āngingis, ānkeris)
    -a:         gen -as,  dat -ai,  akk -an      (Leītawa, ānkstai)
    -i (жен.):  gen -is,  dat -ei,  akk -in      (āuksli)
    Остальные основы (в том числе -ē) остаются в именительном: готового
    шаблона в парадигмах нет, а придумывать формы хуже, чем не склонять.
    """
    low = lemma.lower()
    if low.endswith('is') and len(low) > 3 and gender == 'masc':
        stem = lemma[:-2]
        return {'sg': {'nom': lemma, 'gen': stem + 'jas', 'dat': stem + 'ju', 'akk': stem + 'jan'}}
    if low.endswith('s') and len(low) > 2 and low[-2] not in 'aeiouāēīōū':
        stem = lemma[:-1]
        return {'sg': {'nom': lemma, 'gen': stem + 'as', 'dat': stem + 'u', 'akk': stem + 'an'}}
    if low.endswith('a'):
        stem = lemma[:-1]
        return {'sg': {'nom': lemma, 'gen': stem + 'as', 'dat': stem + 'ai', 'akk': stem + 'an'}}
    if low.endswith('i') and gender == 'fem':
        stem = lemma[:-1]
        return {'sg': {'nom': lemma, 'gen': stem + 'is', 'dat': stem + 'ei', 'akk': stem + 'in'}}
    return {'sg': {'nom': lemma}}


def ru_declension(ru_nom, gender, morph):
    """Русские падежи: pymorphy для узнанных имён, иначе простое правило.

    У незнакомых имён pymorphy угадывает разбор и выдаёт мусор («Бугёсел» из
    «Бугесла»), поэтому для них работает обычное именное склонение.
    """
    # Имена на -и/-е/-о/-у в русском не склоняются («Каисини», «Милагеиди»);
    # pymorphy для таких слов выдаёт множественное число чужого слова.
    if ru_nom[-1].lower() in 'ыеоуиюэ':
        return {k: ru_nom for k in ('nom', 'gen', 'dat', 'akk', 'ins', 'prl')}, 'несклоняемое'

    parses = morph.parse(ru_nom)
    name_parses = [x for x in parses if x.tag.case == 'nomn' and 'Name' in x.tag]
    known = [x for x in parses if x.is_known and 'Name' not in x.tag
             and 'Surn' not in x.tag and 'Patr' not in x.tag]

    if name_parses:
        p = name_parses[0]
        out = {'nom': ru_nom}
        for case, key in (('gent', 'gen'), ('datv', 'dat'), ('accs', 'akk'),
                          ('ablt', 'ins'), ('loct', 'prl')):
            f = p.inflect({case})
            out[key] = (f.word[:1].upper() + f.word[1:]) if f else ru_nom
        return out, ('pymorphy' if not known else 'pymorphy+омоним')

    if ru_nom.endswith('а'):
        stem = ru_nom[:-1]
        tail = 'и' if stem[-1].lower() in 'гкхжчшщ' else 'ы'
        return {'nom': ru_nom, 'gen': stem + tail, 'dat': stem + 'е', 'akk': stem + 'у',
                'ins': stem + 'ой', 'prl': stem + 'е'}, 'правило -а'
    if ru_nom.endswith('й'):
        stem = ru_nom[:-1]
        return {'nom': ru_nom, 'gen': stem + 'я', 'dat': stem + 'ю', 'akk': stem + 'я',
                'ins': stem + 'ем', 'prl': stem + 'е'}, 'правило -й'
    return {'nom': ru_nom, 'gen': ru_nom + 'а', 'dat': ru_nom + 'у', 'akk': ru_nom + 'а',
            'ins': ru_nom + 'ом', 'prl': ru_nom + 'е'}, 'правило -с'


def main():
    dictionary = json.load(open(D + 'dictionary.json', encoding='utf-8'))
    curated = json.load(open(D + 'propernames-curated.json', encoding='utf-8'))
    curated_by_lemma = {e['lemma']: e for e in curated}

    names = [e for e in dictionary
             if (e.get('ru') or '') in ('прусское мужское имя', 'прусское женское имя')]

    sys.path.insert(0, ROOT)
    import pymorphy3
    morph = pymorphy3.MorphAnalyzer()

    out, seen_ru = [], {}
    stats = collections.Counter()
    skipped = []
    for e in names:
        lemma = (e.get('w') or '').strip()
        if not lemma or ' ' in lemma:
            skipped.append((lemma, 'многословная лемма'))
            continue
        gender = 'masc' if e['ru'].endswith('мужское имя') else 'fem'
        ru_nom = translit(lemma)
        if not re.match(r'^[А-ЯЁ][а-яё-]+$', ru_nom):
            skipped.append((lemma, 'транслит не кириллицей: ' + ru_nom))
            continue
        ru_sg, how = ru_declension(ru_nom, gender, morph)
        if how == 'pymorphy+омоним':
            skipped.append((lemma, 'омоним нарицательного: ' + ru_nom))
            continue
        stats[how] += 1
        key = ru_sg['nom'].lower()
        if key in seen_ru:
            stats['дубль по-русски'] += 1
            continue
        seen_ru[key] = lemma

        entry = {'lemma': lemma, 'aliases': [], 'gender': gender, 'priority': 50,
                 'pr': pr_block(lemma, gender), 'ru': {'sg': ru_sg}}
        if lemma in curated_by_lemma:
            entry = curated_by_lemma[lemma]
            stats['курируемая запись сохранена'] += 1
        out.append(entry)
        stats['со склонением' if 'gen' in entry['pr']['sg'] else 'только именительный'] += 1

    have = {e['lemma'] for e in out}
    for lemma, e in curated_by_lemma.items():
        if lemma not in have:
            out.append(e)
            stats['курируемая вне словаря'] += 1

    out.sort(key=lambda x: (x.get('priority', 50), x['lemma']))
    json.dump(out, open(D + 'propernames.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(json.dumps(stats, ensure_ascii=False, indent=1))
    print('всего записей:', len(out), '| пропущено:', len(skipped),
          collections.Counter(r for _, r in skipped).most_common(4))
    for s in skipped[:5]:
        print('   ', s)


if __name__ == '__main__':
    main()
