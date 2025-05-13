import difflib
import logging
import tkinter as tk
from tkinter import ttk

from gui_components import ScrollableListBox, ScrollableTextBox
from webnovels.gui.backend import Backend
from webnovels.utils import get_novel_chapter_titles, get_novel_titles, to_tk_index


class EditorPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.log = logging.getLogger(self.__class__.__name__)

        self.backend = Backend()

        self.novel_selector = None
        self.chapter_selector = None

        self.chapter_text: ScrollableTextBox = None

        self.create_selector_widget()
        self.create_editor_widget()

        self.bind_all("<Control-s>", self._save)
        self.bind_all("<Control-z>", self._undo)
        self.bind_all("<Control-y>", self._redo)

    @property
    def edit_tracker(self):
        return self.backend.edit_tracker

    @property
    def spell_checker(self):
        return self.backend.spell_checker

    def on_novel_title_selection(self, *_):
        self.backend.save()

        novel_title = self.novel_selector.get()
        if novel_title:
            self.chapter_selector.set_options(get_novel_chapter_titles(novel_title))
            self.backend.load_novel(novel_title)
        else:
            self.chapter_selector.delete_all()

    def on_chapter_title_selection(self, *_):
        self.backend.save()

        novel_title = self.novel_selector.get()
        chapter_title = self.chapter_selector.get_value()
        if novel_title and chapter_title:
            self.log.debug(f"Loading chapter '{chapter_title}' from novel '{novel_title}'")
            chapter_text = self.backend.load_chapter(chapter_title)
            self.chapter_text.set(chapter_text)

            errors = self.backend.potential_errors
            for start_index, end_index in errors:
                self.chapter_text.mark_incorrect(to_tk_index(chapter_text, start_index),
                                                 to_tk_index(chapter_text, end_index))

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
        self.backend.undo()
        self.chapter_text.set(self.backend.chapter_text)
        return "break"

    def _redo(self, *_):
        self.log.debug('Redo')
        self.backend.redo()
        self.chapter_text.set(self.backend.chapter_text)
        return "break"

    def _save(self, *_):
        self.log.debug('Save')
        self.backend.save()
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

        # Create the context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Ignore")
        self.context_menu.add_command(label="Add to global dictionary")  # , command=self.backend.add_word(self.chapter_text.get_selected()))
        self.context_menu.add_command(label="Add to local dictionary")

        # Bind right-click to show context menu
        self.chapter_text.textbox.bind("<Button-3>", self.on_right_click, add='+')  # For Windows and Linux
        # self.textbox.bind("<Button-2>", self.show_context_menu)  # For macOS (right-click is <Button-2>)

    def on_right_click(self, event):
        try:
            # Check if there is a selection
            if self.chapter_text.textbox.tag_ranges(tk.SEL):
                self.context_menu.entryconfig("Ignore", state="normal")
                self.context_menu.entryconfig("Add to global dictionary", state="normal")
                self.context_menu.entryconfig("Add to local dictionary", state="normal")
            else:
                # Disable actions that require selection
                self.context_menu.entryconfig("Ignore", state="disabled")
                self.context_menu.entryconfig("Add to global dictionary", state="disabled")
                self.context_menu.entryconfig("Add to local dictionary", state="disabled")

            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def on_text_change(self, event=None):
        self.log.debug(f"Modified: {event}")
        widget = event.widget
        if widget.edit_modified():
            widget.edit_modified(False)  # reset flag

        new_text = self.chapter_text.get()
        old_text = self.backend.chapter_text

        if new_text == old_text:
            return  # No change

        matcher = difflib.SequenceMatcher(None, old_text, new_text)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in ("replace", "delete", "insert"):
                self.log.debug(f"Detected change '{tag}'")
                self.backend.make_edit(
                    start_idx=i1,
                    end_idx=i2,
                    new_text=new_text[j1:j2],
                )
                break  # Only handle the first meaningful change
