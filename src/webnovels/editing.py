import gzip
import json
import logging
import pkgutil
import re
import time
from pathlib import Path

from spellchecker import SpellChecker
from spellchecker.utils import ensure_unicode

from webnovels.utils import NOVELS_DIR, get_chapter_index, get_file_safe, get_novel_dir

ChangeRecord = dict[str, int | str]


class NovelSpellChecker:
    """

    """
    GLOBAL_DICT_EXT = Path(__file__).parent / '.resources' / 'dictionary_ext.txt'
    WHITESPACE = set(' \n\t')

    def __init__(self, novel_title):
        self.log = logging.getLogger(self.__class__.__name__)

        novel_dir = NOVELS_DIR / get_file_safe(novel_title)

        self.LOCAL_DICT_EXT = novel_dir / '.resources' / 'dictionary_ext.txt'

        self._spell = SpellChecker(case_sensitive=True, language=None)

        # Manually load the language file or else we can't do case-sensitive. This will lead to some side effects
        # with proper nouns since the words in the corpus are all lowered.
        # TODO: Fix this?
        filename = f"resources/en.json.gz"
        try:
            json_open = pkgutil.get_data("spellchecker", filename)
        except FileNotFoundError as exc:
            msg = f"The provided dictionary language (en) does not exist!"
            raise ValueError(msg) from exc
        lang_dict = json.loads(gzip.decompress(json_open).decode("utf-8"))
        self._spell.word_frequency.load_json(lang_dict)

        self._spell.word_frequency.load_text_file(self.GLOBAL_DICT_EXT)
        self._spell.word_frequency.load_text_file(self.LOCAL_DICT_EXT)

    def get_potential_errors(self, text):
        whitespace_indices = [i for i, c in enumerate(text) if c in self.WHITESPACE] + [len(text)]

        potential_errors = []
        cleaned_tokens = set()

        start_index = 0
        for end_index in whitespace_indices:
            if start_index == end_index:
                self.log.warning(f"Equal space indices found ({start_index}), continuing")
                continue

            if start_index + 1 == end_index:
                self.log.warning(f"Consecutive spaces found ({start_index, end_index}), continuing")
            else:
                cleaned_tokens.add(self.clean_token(text[start_index:end_index]))
            start_index = end_index + 1

        # TODO: find consecutive space errors

        unknown_words = self._spell.unknown(cleaned_tokens)
        self.log.debug(', '.join(unknown_words))

        # TODO: get index ranges of misspellings

    def flag_misspellings(self, words):
        """The subset of `words` that do not appear in the dictionary

        Args:
            words (list): List of words to determine which are not in the corpus
        Returns:
            set: The set of those words from the input that are not in the corpus"""
        tmp_words = [ensure_unicode(w) for w in words]
        tmp = [w if self._case_sensitive else w.lower() for w in tmp_words if self._check_if_should_check(w)]
        return {w for w in tmp if w not in self._word_frequency.dictionary}

    def clean_token(self, token):
        # Special case: HTML tags
        if '<' in token and '>' in token:
            token = ''.join(re.split(r'<[\/a-z]{,5}>', token))

        # punctuation = '.,!?;:"\'()[]{} -–—…\n‘’“”'
        # strip_chars = '.,!?;:"\'()[]{}…‘’“”'

        allowed_before = '([{‘“'
        allowed_after = '.,!?;:")]}…’”'

        return token.lstrip(allowed_before).rstrip(allowed_after)

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
            previous_end_idx = previous_change["start_idx"] + len(previous_change["new_text"])

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

        self.log.debug(f"Adding change to stack: {change}")
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
        if not self.history:
            return

        self.mergeable = False

        change = self.history.pop()
        self._processed_text = self._apply_inverse(self._processed_text, change)
        self.redo_stack.append(change)

    def redo(self):
        if not self.redo_stack:
            return

        self.mergeable = False

        change = self.redo_stack.pop()
        self._processed_text = self._apply_change(self._processed_text, change)
        self.history.append(change)

    def save(self):
        if not self.change_json_fp:
            return

        self.mergeable = False

        self.log.debug(f"Saving edits to {self.change_json_fp}")
        with open(self.change_json_fp, "w") as change_json:
            json.dump(self.history, change_json, indent=2)

    def load_chapter(self, novel_title, chapter_title):
        self.log.debug(f"Loading chapter '{chapter_title}' from novel '{novel_title}'")
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
            self.log.debug(f"Initialising change list at {self.change_json_fp}")
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
    editor.load_chapter(novel_title, 'Chapter 1: Quicksave')

    speller = NovelSpellChecker(novel_title)
    speller.get_potential_errors(editor.processed_text)
    print(1)
    # novel_spellchecker = get_novel_spellchecker(novel_title)
    # for fname in (novel_dir / 'raw_chapters').glob('*.txt'):
    #     edit_chapter(novel_dir, fname, novel_spellchecker)
