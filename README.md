# dict-ro-ro

Romanian word list for the [ABCx3](https://abcx3.com) crossword game.

## Source

The word list is derived from the **Dexonline LOC (Lista Oficială de Cuvinte)** —
the official word list for Romanian Scrabble tournaments, maintained by the
Romanian Scrabble Federation in collaboration with [dexonline.ro](https://dexonline.ro).

- Source page: <https://dexonline.ro/scrabble>
- GitHub reference: <https://github.com/mgax/dexonline-scrabble>
- Upstream word list: `LOC5.txt` (LOC v5.0)

## License

The Dexonline LOC is published under **GPL 2.0** (or later).

This repository treats the generated word list as a derived work under **GPL 2.0**:

- License page: <https://www.gnu.org/licenses/old-licenses/gpl-2.0.html>
- Attribution: Romanian Scrabble Federation / dexonline.ro

## Why This Source

- **No proper names**: The LOC is specifically curated for competitive Scrabble
  and explicitly excludes proper nouns, abbreviations not used as common words,
  and other non-game-legal entries.
- **All inflections included**: Every inflected form is a separate entry in the
  list (required for word game validation).
- **Tournament standard**: LOC v5.0 contains ~610,000 words and is the reference
  used for official Romanian Scrabble play.
- **High quality**: Maintained and validated by the Romanian Scrabble Federation.

## Processing

The raw LOC word list is processed with `generate_words.py`:

1. Download the LOC word list from dexonline.ro/scrabble.
2. Keep only words that are:
   - All alphabetic Romanian characters (a–z plus diacritics: ă, â, î, ș, ț)
   - 2 to 15 characters long
3. Deduplicate and sort alphabetically.

No additional proper-name filtering is required since the source already
excludes proper names by design.

## Output

- File: `output/words_ro-RO.txt`
- Encoding: UTF-8
- Sorting: alphabetical
- Length bounds: 2–15 characters

## Regenerating

```bash
python3 generate_words.py
```
