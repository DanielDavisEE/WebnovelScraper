import logging
import tkinter as tk
from tkinter import ttk
import difflib

from webnovels.editing import EditTracker
from webnovels.utils import get_novel_titles, get_novel_chapter_titles

from gui_components import ScrollableListBox, ScrollableTextBox


class EditorPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.log = logging.getLogger(self.__class__.__name__)

        self.edit_tracker = EditTracker()

        self.novel_selector = None
        self.chapter_selector = None

        self.chapter_text = None

        self.create_selector_widget()
        self.create_editor_widget()

        self.bind_all("<Control-s>", self._save)
        self.bind_all("<Control-z>", self._undo)
        self.bind_all("<Control-y>", self._redo)

    def on_novel_title_selection(self, *_):
        self.edit_tracker.save()

        novel_title = self.novel_selector.get()
        if novel_title:
            self.chapter_selector.set_options(get_novel_chapter_titles(novel_title))
        else:
            self.chapter_selector.delete_all()

    def on_chapter_title_selection(self, *_):
        self.edit_tracker.save()

        novel_title = self.novel_selector.get()
        chapter_title = self.chapter_selector.get_value()
        if novel_title and chapter_title:
            self.log.debug(f"Loading chapter '{chapter_title}' from novel '{novel_title}'")
            self.edit_tracker.load_chapter(novel_title, chapter_title)
            self.chapter_text.set(self.edit_tracker.processed_text)

    def create_selector_widget(self):
        chapter_select_frame = ttk.Frame(self)
        chapter_select_frame.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False)

        self.novel_selector = ttk.Combobox(chapter_select_frame, values=[''] + get_novel_titles(), exportselection=False)
        self.novel_selector.state(["readonly"])
        self.novel_selector.pack(
            side=tk.TOP, fill=tk.X, expand=False)

        self.chapter_selector = ScrollableListBox(chapter_select_frame, display_rows=20)
        self.chapter_selector.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True)

        # Bind event to handler function
        self.novel_selector.bind("<<ComboboxSelected>>", self.on_novel_title_selection)
        self.chapter_selector.listbox.bind("<<ListboxSelect>>", self.on_chapter_title_selection)

    def _undo(self, *_):
        self.log.debug('Undo')
        self.edit_tracker.undo()
        self.chapter_text.set(self.edit_tracker.processed_text)
        return "break"

    def _redo(self, *_):
        self.log.debug('Redo')
        self.edit_tracker.redo()
        self.chapter_text.set(self.edit_tracker.processed_text)
        return "break"

    def _save(self, *_):
        self.log.debug('Save')
        self.edit_tracker.save()
        return "break"

    def _prev(self, *_):
        self.log.debug('Previous')
        current_index = self.chapter_selector.get()
        if current_index:
            prev_index = current_index[0] - 1
            if 0 <= prev_index < len(self.chapter_selector.get_options()):
                self.chapter_selector.set(prev_index)
        self.on_chapter_title_selection()
        return "break"

    def _next(self, *_):
        self.log.debug('Next')
        current_index = self.chapter_selector.get()
        if current_index:
            next_index = current_index[0] + 1
            if 0 <= next_index < len(self.chapter_selector.get_options()):
                self.chapter_selector.set(next_index)
        self.on_chapter_title_selection()
        return "break"

    def create_editor_widget(self):
        chapter_edit_frame = ttk.Frame(self)
        chapter_edit_frame.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True)

        chapter_view_frame = ttk.Frame(chapter_edit_frame)
        chapter_view_frame.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True)

        self.chapter_text = ScrollableTextBox(chapter_view_frame)
        self.chapter_text.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True)

        edit_options_frame = ttk.Frame(chapter_edit_frame)
        edit_options_frame.pack(
            side=tk.TOP, fill=tk.BOTH, expand=False)

        ttk.Button(edit_options_frame, text='Redo', command=self._redo).grid(
            row=0, column=0, padx=5, pady=5)
        ttk.Button(edit_options_frame, text='Undo', command=self._undo).grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Button(edit_options_frame, text='Save', command=self._save).grid(
            row=0, column=2, padx=5, pady=5)
        ttk.Button(edit_options_frame, text='Previous', command=self._prev).grid(
            row=0, column=3, padx=5, pady=5)
        ttk.Button(edit_options_frame, text='Next', command=self._next).grid(
            row=0, column=4, padx=5, pady=5)

        self.chapter_text.textbox.bind("<<Modified>>", self.on_text_change)
        # self.chapter_text.textbox.bind("<<Paste>>", self.on_text_change)

    def on_text_change(self, event=None):
        self.log.debug(f"Modified: {event}")
        widget = event.widget
        if widget.edit_modified():
            widget.edit_modified(False)  # reset flag

        new_text = self.chapter_text.get()
        old_text = self.edit_tracker.processed_text

        if new_text == old_text:
            return  # No change

        matcher = difflib.SequenceMatcher(None, old_text, new_text)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in ("replace", "delete", "insert"):
                self.log.debug(f"Detected change '{tag}'")
                self.edit_tracker.record_change(
                    start_idx=i1,
                    end_idx=i2,
                    new_text=new_text[j1:j2],
                )
                break  # Only handle the first meaningful change
