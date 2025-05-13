from webnovels.editing import EditTracker, NovelSpellChecker


class Backend:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """ Create class as a singleton """
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.edit_tracker = EditTracker()
        self.spell_checker = NovelSpellChecker()

        self.novel_title = None
        self.chapter_title = None
        self.potential_errors = []
        self.selected_error = None

    @property
    def chapter_text(self):
        return self.edit_tracker.processed_text

    def save(self):
        self.edit_tracker.save()

    def undo(self):
        self.edit_tracker.undo()

    def redo(self):
        self.edit_tracker.undo()

    def load_novel(self, novel_title):
        self.novel_title = novel_title

        self.spell_checker.load_novel(novel_title)

    def load_chapter(self, chapter_title):
        self.chapter_title = chapter_title

        self.edit_tracker.load_chapter(self.novel_title, self.chapter_title)
        self.potential_errors = self.spell_checker.get_potential_errors(self.edit_tracker.processed_text)

        return self.chapter_text

    def make_edit(self, start_idx: int, end_idx: int, new_text: str):
        self.edit_tracker.record_change(start_idx, end_idx, new_text)
        # FIXME: updated potential errors (when necessary?)

    def add_word(self, word, local=True):
        self.spell_checker.add_word(word, local)
