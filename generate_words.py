#!/usr/bin/env python3
"""
Generates a clean Romanian word list from the wooorm/dictionaries hunspell
dictionary (ro_RO.aff + ro_RO.dic).

Processing steps:
1. Parse ro_RO.aff: extract AF (alias flag) mappings and SFX (suffix) rules
2. Parse ro_RO.dic: iterate all entries
3. For each lowercase entry, apply applicable SFX rules
4. Filter: only Romanian alphabet letters (a ă â b c d e f g h i î j k l m n o p r s ș t ț u v x z),
   length 2–15 characters, no hyphens, no abbreviations
5. Sort and deduplicate the output

Output: romanian_ro_ro_hunspell.txt — expanded Romanian word forms
"""

import re
import sys
import subprocess
import os
from collections import defaultdict

# Valid Romanian characters (the Romanian Scrabble alphabet - note: no q, w, y)
# ș uses Unicode U+0219, ț uses Unicode U+021B (correct Romanian chars, not Turkish ş/ţ)
VALID_CHARS = frozenset('aăâbcdefghiîjklmnoprstșțuvxz')
VOWELS = frozenset('aăâeîiou')

MAX_WORD_LEN = 15   # Maximum word length for the game dictionary
MIN_WORD_LEN = 2    # Minimum word length


def is_valid_ro_word(word: str) -> bool:
    """Return True if word contains only valid Romanian characters and is in range."""
    return (MIN_WORD_LEN <= len(word) <= MAX_WORD_LEN
            and all(c in VALID_CHARS for c in word))


def has_vowel(word: str) -> bool:
    """Return True if word contains at least one vowel."""
    return any(c in VOWELS for c in word)


def parse_aff(aff_path: str):
    """
    Parse the Hunspell .aff file.

    Returns:
        af_aliases: dict[int, bytes] — AF alias number → raw flag bytes
        sfx_rules: dict[bytes, list] — flag byte → [(strip, add, condition_re)]
        needaffix_flag: bytes | None — the NEEDAFFIX flag byte
        forbiddenword_flag: bytes | None — the FORBIDDENWORD flag byte
    """
    with open(aff_path, 'rb') as f:
        content = f.read()

    lines = content.split(b'\n')
    af_aliases: dict = {}
    af_idx = 0
    sfx_rules: defaultdict = defaultdict(list)
    needaffix_flag = None
    forbiddenword_flag = None

    for line in lines:
        if b'#' in line:
            line = line[:line.index(b'#')]
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if not parts:
            continue
        directive = parts[0]

        if directive == b'AF':
            if len(parts) >= 2 and not parts[1].isdigit():
                af_idx += 1
                af_aliases[af_idx] = parts[1]

        elif directive == b'NEEDAFFIX':
            if len(parts) >= 2:
                needaffix_flag = parts[1]

        elif directive == b'FORBIDDENWORD':
            if len(parts) >= 2:
                forbiddenword_flag = parts[1]

        elif directive == b'SFX':
            if len(parts) >= 5:
                flag_b = parts[1]
                strip = parts[2].decode('utf-8', errors='replace')
                add_raw = parts[3].decode('utf-8', errors='replace')
                condition = parts[4].decode('utf-8', errors='replace')

                # Extract just the word part (before any /flag)
                add_word = add_raw[:add_raw.index('/')] if '/' in add_raw else add_raw

                if strip == '0':
                    strip = ''
                if add_word == '0':
                    add_word = ''

                # Skip suffix rules that add hyphens (compound prefixes)
                if '-' in add_word:
                    continue

                # Precompile condition regex
                try:
                    cond_re = None if condition == '.' else re.compile(condition + '$')
                except re.error:
                    continue

                sfx_rules[flag_b].append((strip, add_word, cond_re))

    return af_aliases, sfx_rules, needaffix_flag, forbiddenword_flag


def expand_dictionary(aff_path: str, dic_path: str, output_path: str) -> int:
    """
    Expand all word forms and write to output_path.
    Returns number of unique words written.
    """
    print("Parsing .aff file...", file=sys.stderr, flush=True)
    af_aliases, sfx_rules, needaffix_flag, forbiddenword_flag = parse_aff(aff_path)
    print(f"  {len(af_aliases)} AF aliases, {len(sfx_rules)} SFX flag groups", file=sys.stderr, flush=True)

    print("Parsing .dic file...", file=sys.stderr, flush=True)
    with open(dic_path, 'r', encoding='utf-8', errors='replace') as f:
        dic_lines = f.readlines()[1:]  # skip count line
    print(f"  {len(dic_lines)} entries in .dic", file=sys.stderr, flush=True)

    temp_path = output_path + '.tmp'
    total_written = 0
    forbidden_words: set = set()

    print("Expanding inflected forms (streaming to disk)...", file=sys.stderr, flush=True)

    with open(temp_path, 'w', encoding='utf-8') as out:
        for idx, line in enumerate(dic_lines):
            line = line.strip()
            if not line:
                continue

            # Strip frequency tab data
            if '\t' in line:
                line = line.split('\t')[0]

            # Parse word and flags
            if '/' in line:
                slash_idx = line.index('/')
                word = line[:slash_idx].replace('\\/', '/')
                flags_str = line[slash_idx + 1:]
                try:
                    flags_num = int(flags_str)
                    flag_bytes = af_aliases.get(flags_num, b'')
                except ValueError:
                    flag_bytes = flags_str.encode('utf-8', errors='replace')
            else:
                word = line
                flag_bytes = b''

            # Skip: spaces, leading hyphens, or uppercase first letter (proper nouns)
            if ' ' in word or word.startswith('-') or (word and word[0].isupper()):
                continue

            word_lower = word.lower()

            if not is_valid_ro_word(word_lower):
                continue

            # Check special flags
            has_needaffix = False
            has_forbidden = False
            for fb in flag_bytes:
                fb_b = bytes([fb])
                if forbiddenword_flag and fb_b == forbiddenword_flag:
                    has_forbidden = True
                if needaffix_flag and fb_b == needaffix_flag:
                    has_needaffix = True

            if has_forbidden:
                forbidden_words.add(word_lower)
                continue

            # Write base form (unless NEEDAFFIX)
            if not has_needaffix:
                out.write(word_lower + '\n')
                total_written += 1

            # Apply SFX rules for each flag byte
            for fb in flag_bytes:
                flag_b = bytes([fb])
                if flag_b not in sfx_rules:
                    continue
                for strip, add, cond_re in sfx_rules[flag_b]:
                    # Condition check
                    if cond_re and not cond_re.search(word_lower):
                        continue
                    # Apply strip
                    if strip:
                        if not word_lower.endswith(strip):
                            continue
                        stem = word_lower[:-len(strip)]
                    else:
                        stem = word_lower
                    # Build new word
                    new_word = stem + add
                    if is_valid_ro_word(new_word):
                        out.write(new_word + '\n')
                        total_written += 1

            if (idx + 1) % 20000 == 0:
                print(f"  {idx+1}/{len(dic_lines)} entries processed, {total_written} forms written", file=sys.stderr, flush=True)

    print(f"\nRaw forms: {total_written}", file=sys.stderr, flush=True)
    print("Sorting, deduplicating, and removing abbreviations...", file=sys.stderr, flush=True)

    # Sort + uniq
    sorted_path = output_path + '.sorted'
    subprocess.run(f"sort -u {temp_path} > {sorted_path}", shell=True, check=True)
    os.unlink(temp_path)

    # Final pass: remove consonant-only 2-char words (abbreviations like cm, kg, dz)
    final_count = 0
    with open(sorted_path, 'r', encoding='utf-8') as inp, \
         open(output_path, 'w', encoding='utf-8') as out:
        for line in inp:
            word = line.rstrip('\n')
            if len(word) == 2 and not has_vowel(word):
                continue  # Skip: consonant-only 2-char abbreviation
            if word in forbidden_words:
                continue
            out.write(word + '\n')
            final_count += 1

    os.unlink(sorted_path)
    print(f"Final unique words: {final_count}", file=sys.stderr, flush=True)
    return final_count


if __name__ == '__main__':
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Expected: ro_RO.aff and ro_RO.dic in the data/ subdirectory
    aff_path = os.path.join(script_dir, 'data', 'ro_RO.aff')
    dic_path = os.path.join(script_dir, 'data', 'ro_RO.dic')
    os.makedirs(os.path.join(script_dir, 'output'), exist_ok=True)
    output_path = os.path.join(script_dir, 'output', 'romanian_ro_ro_hunspell.txt')

    if not os.path.exists(aff_path) or not os.path.exists(dic_path):
        print(f"ERROR: ro_RO.aff and ro_RO.dic must be in {script_dir}/data/", file=sys.stderr)
        print("Download from: https://github.com/wooorm/dictionaries", file=sys.stderr)
        sys.exit(1)

    count = expand_dictionary(aff_path, dic_path, output_path)
    print(f"\nDone. Wrote {count} words to {output_path}", file=sys.stderr)
