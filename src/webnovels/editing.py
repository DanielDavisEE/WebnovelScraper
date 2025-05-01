import json
import re
from contextlib import contextmanager
from pathlib import Path

import docx
from bs4 import BeautifulSoup

from spellchecker import SpellChecker

from webnovels.utils import NOVELS_DIR, get_file_safe

GLOBAL_RESOURCES = Path(__file__).parent / '.resources'

# @contextmanager
# def get_resources(resource_dir: Path):
#     assert resource_dir.name == '.resources'
#
#     with open(resource_dir / 'dictionary_ext.txt', 'r') as dictionary_file:
#         dictionary_ext = dictionary_file.readlines()
#     with open(resource_dir / 'word_swaps.json', 'r') as word_swaps_file:
#         word_swaps = json.load(word_swaps_file)
#
#     try:
#         yield dictionary_ext, word_swaps
#
#     finally:
#         with open(resource_dir / 'dictionary_ext.txt', 'r') as dictionary_file:
#             dictionary_file.write('\n'.join(dictionary_ext))
#         with open(resource_dir / 'word_swaps.json', 'r') as word_swaps_file:
#             json.dump(word_swaps, word_swaps_file, indent=2)

def tokenize(text):
    tokens = []
    current_token = ''
    i = 0
    punctuation = set('.,!?;:"\'()[]{} -–—…\n‘’“”')

    while i < len(text):
        char = text[i]

        if char.isspace():
            if current_token:
                tokens.append(current_token)
                current_token = ''
            i += 1
        elif char in punctuation:
            if current_token:
                tokens.append(current_token)
                current_token = ''
            # Handle paired quotes as separate tokens
            tokens.append(char)
            i += 1
        else:
            current_token += char
            i += 1

    if current_token:
        tokens.append(current_token)

    return tokens

def correct_token(token, spell_checker):
    isolated_word = token

    # Special case: HTML tags
    if '<' in token and '>' in token:
        isolated_word = ''.join(re.split(r'<[\/a-z]{,5}>', isolated_word))

    punctuation = '.,!?;:"\'()[]{} -–—…\n‘’“”'
    isolated_word = isolated_word.strip(punctuation)

    if isolated_word:
        misspelt_word = spell_checker.unknown([isolated_word])
        if misspelt_word:
            misspelt_word = misspelt_word.pop()
            possible_corrections = list(spell_checker.candidates(misspelt_word))
            print(f'Identified spelling error: {misspelt_word}')
            print('Options:')
            print(' 1. Add to global dict')
            print(' 2. Add to novel dict')
            print(' 3. Custom correction')
            for i, correction in enumerate(possible_corrections, start=4):
                print(f' {i}. {correction}')
            answer = int(input(''))
            if answer in [1, 2]:
                correct_word = misspelt_word
            elif answer == 3:
                correct_word = input('Custom correction: ')
            elif answer - 4 < len(possible_corrections):
                correct_word = possible_corrections[answer - 4]
            else:
                raise RuntimeError
        else:
            correct_word = isolated_word
    else:
        correct_word = ''

    return token.replace(isolated_word, correct_word)


def edit_chapter(novel_dir, fname, spell_checker):
    with open(novel_dir / 'raw_chapters' / fname) as raw_chapter_file:
        raw_chapter = raw_chapter_file.read()

    processed_chapter = []
    initial_spaces = raw_chapter.count(' ')
    for token in raw_chapter.split(' '):
        processed_chapter.append(correct_token(token, spell_checker))
    processed_chapter = ' '.join(processed_chapter)

    if initial_spaces != processed_chapter.count(' '):
        raise RuntimeError('Discrepancy in number of spaces')
    return processed_chapter

def edit_novel(novel_name):
    novel_dir = NOVELS_DIR / get_file_safe(novel_name)

    spell = SpellChecker()
    spell.word_frequency.load_text_file(GLOBAL_RESOURCES / 'dictionary_ext.txt')
    spell.word_frequency.load_text_file(novel_dir / '.resources' / 'dictionary_ext.txt')

    for fname in (novel_dir / 'raw_chapters').glob('*.txt'):
        edit_chapter(novel_dir, fname, spell)


"""
chapter_dict = {}
chapter_template = {
    'title': None,
    'url': None,
    'soup_object': None,
    'text': None
}

# Get list of chapter pages from index
for chapter in alist:
    link = chapter.get('href')
    tmp = chapter.string.strip(' \n\t').split(' ')
    i, chapter_name = int(tmp[1].strip(':')), ' '.join(tmp[2:])

    try:
        tmp = chapter_name.index('Only')
    except ValueError:
        pass
    else:
        chapter_name = chapter_name[:tmp]

    chapter_name = chapter_name.strip('1234567890/ ()-')

    if chapter_name == '':
        chapter_name = None

    chapter_dict[i] = chapter_template.copy()
    chapter_dict[i]['title'] = chapter_name
    chapter_dict[i]['url'] = link
    print(i, chapter_name, link)

chapter_count = len(chapter_dict)

# Extract text from chapter pages
i = 0 if CHAPTER_LIMIT == 0 else chapter_count - CHAPTER_LIMIT
for chapter in chapter_dict.values():
    i += 1
    invalid_symbols = "\\/?%*:|\"<>."
    fix_fn = lambda s: 'TBD' if chapter['title'] == None else s.translate({ord(j): None for j in invalid_symbols})
    chapter['title'] = fix_fn(chapter['title'])
    with open(f"{TITLE}\\Pages\\{i}. {chapter['title']}.txt",
              'r', encoding='utf-8') as infile:
        chapter['soup_object'] = BeautifulSoup(infile.read(), features="lxml")
    text_area = chapter['soup_object'].find(class_="content-area")

    print(f'\n{i}, {chapter["title"]}')
    # chapter['title'] = spell_dict.fixCommonErrors([chapter['title'])[0]
    # chapter['text'] = spell_dict.fixCommonErrors(simplifyText(text_area))
    chapter['text'] = simplifyText(text_area)
    if chapter['text'] == '':
        raise ValueError(f'Text class incorrectly configured. No text returned for chapter {i}')




def compact_chapters(chapter_dict):
    # Compact chapters
    chapter_dict_tmp = {}
    dummy_chapter = chapter_template.copy()
    dummy_chapter['title'] = ''
    i = 1
    for chapter in chapter_dict.values():
        name_curr = chapter['title']

        name_prev = chapter_dict_tmp.get(i - 1, dummy_chapter)['title']

        # Remove 'The ' from beginning of chapter titles for consistancy
        if len(name_prev) >= 4 and name_prev[:4] == 'The ':
            name_prev = name_prev[4:]
        if len(name_curr) >= 4 and name_curr[:4] == 'The ':
            name_curr = name_curr[4:]

        # If the chapter title is a repeat, append text to previous chapter
        if name_prev.strip('!') == name_curr.strip('!') and name_curr != 'TBD':
            chapter_dict_tmp[i - 1]['text'] += chapter['text']
        else:
            chapter_dict_tmp[i] = chapter
            i += 1

    chapter_dict = chapter_dict_tmp
"""

if __name__ == '__main__':
    novel_title = "The Perfect Run"
    edit_novel(novel_title)