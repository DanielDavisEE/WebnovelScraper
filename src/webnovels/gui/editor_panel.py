import logging
import tkinter as tk
from tkinter import ttk

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

    def on_novel_title_selection(self, *_):
        novel_title = self.novel_selector.get()
        if novel_title:
            self.chapter_selector.set_options(get_novel_chapter_titles(novel_title))
        else:
            self.chapter_selector.delete_all()

    def on_chapter_title_selection(self, *_):
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

        self.novel_selector = ttk.Combobox(chapter_select_frame, values=[''] + get_novel_titles())
        self.novel_selector.state(["readonly"])
        self.novel_selector.pack(
            side=tk.TOP, fill=tk.X, expand=False)

        self.chapter_selector = ScrollableListBox(chapter_select_frame, display_rows=20)
        self.chapter_selector.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True)

        # Bind event to handler function
        self.novel_selector.bind("<<ComboboxSelected>>", self.on_novel_title_selection)
        self.chapter_selector.listbox.bind("<<ListboxSelect>>", self.on_chapter_title_selection)

    def _undo(self):
        self.edit_tracker.undo()
        self.chapter_text.set(self.edit_tracker.processed_text)

    def _redo(self):
        self.edit_tracker.redo()
        self.chapter_text.set(self.edit_tracker.processed_text)

    def _save(self):
        self.edit_tracker.save()

    def _prev(self):
        current_index = self.chapter_selector.get()
        if current_index:
            prev_index = current_index[0] - 1
            if 0 <= prev_index < len(self.chapter_selector.get_options()):
                self.chapter_selector.set(prev_index)
        self.on_chapter_title_selection()

    def _next(self):
        current_index = self.chapter_selector.get()
        if current_index:
            next_index = current_index[0] + 1
            if 0 <= next_index < len(self.chapter_selector.get_options()):
                self.chapter_selector.set(next_index)
        self.on_chapter_title_selection()

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

        ttk.Button(edit_options_frame, text='Redo').grid(
            row=0, column=0, padx=5, pady=5)
        ttk.Button(edit_options_frame, text='Undo').grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Button(edit_options_frame, text='Save').grid(
            row=0, column=2, padx=5, pady=5)
        ttk.Button(edit_options_frame, text='Previous', command=self._prev).grid(
            row=0, column=3, padx=5, pady=5)
        ttk.Button(edit_options_frame, text='Next', command=self._next).grid(
            row=0, column=4, padx=5, pady=5)




class HistoryEditorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor with Change Tracking")
        self.geometry("600x400")

        self.tracker = EditTracker()

        self.text = tk.Text(self, wrap="word", undo=False)
        self.text.pack(fill="both", expand=True)

        self.text.bind("<<Modified>>", self.on_modified)
        self.bind("<Control-z>", self.undo)
        self.bind("<Control-y>", self.redo)

        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Save History", command=self.save_history)
        file_menu.add_command(label="Load History", command=self.load_history)
        self.menu.add_cascade(label="File", menu=file_menu)

    def get_index_for_offset(self, offset):
        return self.text.index(f"1.0 + {offset} chars")

    def on_modified(self, event=None):
        self.text.edit_modified(False)
        current = self.text.get("1.0", "end-1c")
        self.tracker.record_change(self.tracker.last_text, current, self.get_index_for_offset)

    def undo(self, _=None):
        self.tracker.undo(self.text)

    def redo(self, _=None):
        self.tracker.redo(self.text)

    def save_history(self):
        self.tracker.save("edit_history.json")

    def load_history(self):
        self.tracker.load("edit_history.json", self.text)
