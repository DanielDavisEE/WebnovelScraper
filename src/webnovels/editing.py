import json
import logging
import re
import time
from pathlib import Path

from spellchecker import SpellChecker

from webnovels.utils import NOVELS_DIR, get_chapter_index, get_file_safe, get_novel_dir

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
    strip_chars = set('.,!?;:"\'()[]{}…‘’“”')

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
    strip_chars = '.,!?;:"\'()[]{}…‘’“”'
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


ChangeRecord = dict[str, int | str]


class NovelSpellChecker:
    """

    """
    GLOBAL_DICT_EXT = GLOBAL_RESOURCES / 'dictionary_ext.txt'

    def __init__(self, novel_title):
        novel_dir = NOVELS_DIR / get_file_safe(novel_title)

        self.LOCAL_DICT_EXT = novel_dir / '.resources' / 'dictionary_ext.txt'

        self._spell = SpellChecker()
        self._spell.word_frequency.load_text_file(self.GLOBAL_DICT_EXT)
        self._spell.word_frequency.load_text_file(self.LOCAL_DICT_EXT)

    def get_potential_errors(self, text):
        space_indices = [i for i, c in enumerate(text) if c == ' ']

        # Also get consecutive white space

    def clean_token(self, text, start_index, end_index):
        token = text[start_index:end_index]

        # Special case: HTML tags
        if '<' in token and '>' in token:
            token = ''.join(re.split(r'<[\/a-z]{,5}>', token))

        # punctuation = '.,!?;:"\'()[]{} -–—…\n‘’“”'
        # strip_chars = '.,!?;:"\'()[]{}…‘’“”'

        allowed_before = '([{‘“'
        allowed_after = '.,!?;:")]}…’”'

        isolated_word = token.lstrip(allowed_before).rstrip(allowed_after)

    def candidates(self, word):
        return self._spell.candidates(word)

    def add_word(self, word, local=True):
        self._spell.word_frequency.add(word)
        if local:
            with open(self.LOCAL_DICT_EXT, 'a') as dict_ext:
                dict_ext.write(word)
        else:
            with open(self.GLOBAL_DICT_EXT, 'a') as dict_ext:
                dict_ext.write(word)


class EditTracker:
    """
    # A single change record
    {
        "start_idx": start_idx,
        "old_text": "some text",  # The text deleted
        "new_text": "some text",  # The text inserted
        "edit_ts": 1234567890     # Time of edit
    }

    """
    MERGE_TIME_LIMIT = 60

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

        self.history: list[ChangeRecord] = []  # AKA undo_stack
        self.redo_stack: list[ChangeRecord] = []
        self.mergeable: bool = False  # Flag which indicates the next change may be merged into the previous

        self.change_json_fp: Path = None
        self._raw_text: str = None
        self._processed_text: str = None

    @property
    def raw_text(self) -> str:
        return self._raw_text

    @property
    def processed_text(self) -> str:
        # return self.apply_changelist(self.raw_text, self.history)
        return self._processed_text

    def record_change(self, start_idx: int, end_idx: int, new_text: str):
        """
        Record a new text change and optionally merge with the previous one
        if it's a consecutive edit (e.g., typing characters sequentially).
        """
        if self.processed_text[start_idx:end_idx] == new_text:
            self.log.warning("Skipping identical change")
            return

        change = {
            "start_idx": start_idx,
            "old_text": self._processed_text[start_idx:end_idx],
            "new_text": new_text,
            "edit_ts": time.time(),
        }
        self._processed_text = self._apply_change(self._processed_text, change)

        # Try to merge with the previous change if applicable
        if self.history:
            previous_change = self.history[-1]
            previous_end_idx = previous_change["index"] + len(previous_change["new_text"])

            # Prevent change merging if time limit is exceeded
            if change["edit_ts"] - previous_change["edit_ts"] > self.MERGE_TIME_LIMIT:
                self.mergeable = False

            if self.mergeable and previous_end_idx == start_idx:
                self.log.info("Merging consecutive edit")

                # Overwrite change with the merged change
                change = {
                    "start_idx": previous_change["start_idx"],
                    "old_text": previous_change["old_text"] + change["old_text"],
                    "new_text": previous_change["new_text"] + change["new_text"],
                    "edit_ts": time.time(),
                }
                self.history.pop()

        self.history.append(change)
        self.redo_stack.clear()

        self.mergeable = True

    def _apply_change(self, text: str, change: ChangeRecord) -> str:
        # Calculate the end index from the text string to skip the calculation in _apply_inverse
        start_idx, end_idx = change["start_idx"], change["start_idx"] + len(change["old_text"])
        return text[:start_idx] + change["new_text"] + text[end_idx:]

    def _apply_changelist(self, text: str, changelist: list[ChangeRecord]):
        processed_text = text[:]
        for change in changelist:
            processed_text = self._apply_change(processed_text, change)
        return processed_text

    def _apply_inverse(self, text: str, change: ChangeRecord):
        inverse_change = {
            "start_idx": change["start_idx"],
            "old_text": change["new_text"],
            "new_text": change["old_text"],
        }
        return self._apply_change(text, inverse_change)

    def undo(self):
        self.mergeable = False

        if not self.history:
            return
        change = self.history.pop()
        self._processed_text = self._apply_inverse(self._processed_text, change)
        self.redo_stack.append(change)

    def redo(self):
        self.mergeable = False

        if not self.redo_stack:
            return
        change = self.redo_stack.pop()
        self._processed_text = self._apply_change(self._processed_text, change)
        self.history.append(change)

    def save(self):
        self.mergeable = False

        with open(self.change_json_fp, "w") as change_json:
            json.dump(self.history, change_json, indent=2)

    def load_chapter(self, novel_title, chapter_title):
        self.mergeable = False

        novel_dir = get_novel_dir(novel_title)
        chapter_idx = get_chapter_index(novel_title, chapter_title)

        with open(novel_dir / "raw_chapters" / f"{chapter_idx}.txt", "r") as txt_file:
            self._raw_text = txt_file.read()

        self.change_json_fp = novel_dir / "change_lists" / f"{chapter_idx}.json"
        if self.change_json_fp.exists():
            with open(self.change_json_fp, "r") as change_json:
                self.history = json.load(change_json)
        else:
            self.history = []
            with open(self.change_json_fp, "x") as change_json:
                json.dump(self.history, change_json)

        self._processed_text = self._apply_changelist(self.raw_text, self.history)
        self.redo_stack = []


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
    novel_dir = NOVELS_DIR / get_file_safe(novel_title)
    editor = EditTracker()
    print(1)
    # novel_spellchecker = get_novel_spellchecker(novel_title)
    # for fname in (novel_dir / 'raw_chapters').glob('*.txt'):
    #     edit_chapter(novel_dir, fname, novel_spellchecker)
