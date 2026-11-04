# Hermes Translation Phrasebook Improvements

## Overview
Skills and patterns for improving Prussian→Russian and Russian→Prussian translation quality via phrasebook data, key normalization, and multi-sentence handling.

## Always-on Rules
- Phrasebook keys with internal punctuation (commas, dashes) must be normalized via `_norm_ru_key()` / `_norm_pr_key()` before indexing, so that `..., hvor var skrevet, at ...` and the same text without commas map to the same key.
- One-word phrasebook entries (`Ahā`, `Jā`, `Kwēi`, `ēngliskai`) must be checked inside `translate_sentence_json()` and `translate_pr_sentence_json()` before falling through to dictionary lookup, so they work within longer text.
- Multi-sentence input (`pr1 pr2`) must skip internal punctuation when building phrase keys and only stop at sentence boundaries (`.`, `!`, `?`).
- Numerals (`en 1273 mettan`, `Kelli mettans`) govern the number and case of the following word via `_numeral_governs()`: year-range numerals take singular, `1` takes singular, others take plural with accusative case.
- Propername RU→PR lookup uses `_ru_name_index` built from `propernames.json` `ru` field; surface form case is preserved if token starts with uppercase.

## Key Procedures

### Normalizing Phrasebook Keys

1. `_norm_ru_key(text)`:
   - Call `_clean_ru_chunk(text)` to strip non-RU characters
   - Replace all non-word/non-dash sequences with spaces: `re.sub(r"[^\wа-яё-]+", " ", text, flags=re.UNICODE)`
   - Collapse whitespace: `re.sub(r"\s+", " ", key).strip()`

2. `_norm_pr_key(text)`:
   - Call `_clean_pr_phrase(text)` first
   - While ` - ` appears in key, replace with single space: `key = key.replace(" - ", " ")`
   - Strip and return

### Multi-Sentence Phrase Processing

1. In `translate_sentence_json()` and `translate_pr_sentence_json()`:
   - Build `pb_parts` by iterating tokens, skipping `PUNCT_TOKEN_RE` entries that are NOT `.`, `!`, `?`
   - Stop at sentence boundary when a `.`, `!`, `?` punctation is encountered
   - For each size from `len(pb_parts)` down to 2:
     - Build phrase key as `" ".join(pb_parts[:size])`
     - Look up in `_pr_phrasebook` (or folded version via `fold_diacritics`)
     - If found, return with proper end position and source reconstruction
   - Fall back to dictionary `_lookup_pr()` for multi-word entries without comma/dash handling.

### Numeral Government

1. `_numeral_governs(value, next_lemma)`:
   - If `YEAR_MIN <= value <= YEAR_MAX` and `next_lemma` is in `YEAR_LEMMAS` (`{год, года, году, годом, годе, leta, let}`): return `("sg", None)`
   - If `value == 1`: return `("sg", None)`
   - Otherwise: return `("pl", "akk")`

2. In `translate_sentence_json()` / `translate_pr_sentence_json()`:
   - After parsing a noun/NPRO token with `pending_numeral` set:
     - Call `_numeral_governs(pending_numeral, parse.normal_form)`
     - Set `agreement = {"number": num}`
     - If `case_hint` is set and no `effective_case`, set `agreement["case"] = case_hint`

### Propername RU→PR Lookup

1. `_render_propername_ru_to_pr(token, forced_case=None, agreement=None)`:
   - Look up `_ru_name_index.get(_clean_ru_token(token))`
   - If hit: extract `entry`, `num`, `ru_case`
   - Determine `surface_ru_case = _PR_CASE_TO_RU.get(ru_case, "nomn")`
   - If `surface_ru_case == "nomn"` and `forced_case` is set: use `forced_case` instead
   - Look up `pr_case = _RU_TO_PR_CASE.get(target_ru_case, "nom")`
   - Get form from `pr[num][pr_case]` (fallback to `pr["sg"][pr_case]`)
   - If form is list: use `_closest_variant(lemma, form)` to pick best match
   - If token starts with uppercase: capitalize first letter of form
   - Return formed string or `None` if not found

2. `_closest_variant(lemma, variants)`:
   - Score each variant by longest common prefix with `lemma.lower()`
   - Return the highest-scoring variant, or `None` if no variants

## Pitfalls to Remember

- **Pitfall: Internal punctuation breaks phrasebook indexing** — Without `_norm_ru_key()` / `_norm_pr_key()`, phrases with commas/dashes inside them create separate keys and fail to match on re-entry.
- **Pitfall: One-word phrasebook entries silent outside standalone mode** — `Ahā`, `Jā` etc. only translate when checked before dictionary fallback in `translate_word()` / `translate_pr_word()`.
- **Pitfall: Multi-sentence input splits on commas/dashes inside phrases** — Without the `while " - " in key` loop in `_norm_pr_key()`, `As bilāi: - Kāigi` and `As bilāi Kāigi` get different keys.
- **Pitfall: `aulaūwuns` forms without "participles" label** — The participle block must also check `entry.get("w", "").endswith("uns")` to handle dictionary headwords ending in `-uns`.
- **Pitfall: Year numerals taking genitive instead of accusative** — Without the `YEAR_LEMMAS` check in `_numeral_governs()`, `en 1273 mettan` incorrectly produces `В 1273 годах` instead of `В 1273 году`.

## Decision Table: Phrase Key Normalization

| Input RU Phrase | `_norm_ru_key()` Output | Match? |
|---|---|---|
| `добрый день` | `добрый день` | Yes (standalone) |
| `доброго дня` | `доброго дня` | Yes (standalone); also matches if added as alternate key |
| `по легендам Тевтонского ордена` | `по легендам тевтонского ордена` | Yes |
| `я видел статью, где было написано, что балтийские языки` | `я видел статью где было написано что балтийские языки` | Yes (commas removed) |
| `As bilāi: - Kāigi` | `As bilāi Kāigi` | Yes (dash + space collapsed) |
| `As bilāi Kāigi` | `As bilāi Kāigi` | Yes |
| `\n` (newline in key) | spaces collapsed | Yes |

## References Files (to be created in references/ directory)

- `references/phrasebook-normalization.md` — detailed examples and edge cases for `_norm_ru_key()` / `_norm_pr_key()`
- `references/numeral-government-recipes.md` — test scripts for numeral government patterns
- `references/propername-ru-to-pr-guide.md` — construction guide for `_ru_name_index` and case mapping
- `references/multi-sentence-recipes.md` — reproduction recipes for multi-sentence phrase matching

## Related Skills

- `hermes-agent` — general Hermes agent configuration and operation (separate skill)
- `nous-batch-gloss-improvement` — batch gloss improvement (separate skill, not loaded due to content loss)