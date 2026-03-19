# dict-ro-ro

Romanian word list for the [ABCx3](https://abcx3.com) crossword game.

## Source

The word list is derived from the **Hunspell Romanian Dictionary** (`ro_RO`),
the standard Romanian spell-checking dictionary maintained by the Rospell Team
and distributed as part of LibreOffice and Firefox.

- GitHub (via wooorm/dictionaries): <https://github.com/wooorm/dictionaries/tree/main/dictionaries/ro>
- Original maintainer: Rospell Team

The dictionary consists of a root word list (`ro_RO.dic`) and a comprehensive
set of morphological affix rules (`ro_RO.aff`) that generate all inflected
forms for Romanian nouns, verbs, and adjectives.

## License

The Hunspell Romanian dictionary is tri-licensed under
**GPL 2.0 / LGPL 2.1 / MPL 1.1** — the user may choose which license applies.

This repository uses the dictionary data under **MPL 1.1 (Mozilla Public License 1.1)**:

- License page: <https://www.mozilla.org/en-US/MPL/1.1/>
- Attribution: Rospell Team

MPL 1.1 is a file-level copyleft license. Modifications to the dictionary
files themselves must be shared, but the game source code is not affected.
The generated word list is distributed under MPL 1.1 alongside the game.

## Why This Source

- **Tri-license flexibility**: MPL 1.1 chosen as the cleanest option for
  commercial use — file-level copyleft only, does not affect game code.
- **Comprehensive inflections**: The `.aff` affix rules cover all Romanian
  noun declensions, verb conjugations, and adjective forms.
- **Widely used**: Same dictionary used by LibreOffice and Firefox for
  Romanian spell-checking.
- **Note**: The Dexonline LOC (the official Romanian Scrabble word list) is
  GPL v2+ / AGPL v3+, which is too restrictive for this use case.

## Processing

The word list is generated with `generate_words.py`:

1. Download `ro_RO.dic` and `ro_RO.aff` from the source.
2. Expand all Hunspell affix rules to generate inflected surface forms.
3. Filter out entries marked as proper nouns (capitalised root words in `.dic`).
4. Keep only words that are:
   - All alphabetic Romanian characters (a–z plus diacritics: ă, â, î, ș, ț)
   - 2 to 15 characters long
5. Deduplicate and sort alphabetically.

## Output

- File: `output/words_ro-RO.txt`
- Encoding: UTF-8
- Sorting: alphabetical
- Length bounds: 2–15 characters
- Download: <https://dictionaries.abcx3.com/romanian_ro_ro_hunspell.txt>

## Regenerating

```bash
python3 generate_words.py
```
