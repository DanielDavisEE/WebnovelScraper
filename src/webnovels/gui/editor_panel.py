import tkinter as tk
from tkinter import ttk

from webnovels.editing import EditTracker
from webnovels.utils import get_chapter_text, get_novel_chapter_titles, get_novel_titles

from gui_components import ScrollableListBox, ScrollableTextBox


class EditorPanel(ttk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent)

        self.shared_data = shared_data

        self.novel_selector = None
        self.chapter_selector = None

        self.chapter_text = None

        self.create_selector_widget()
        self.create_editor_widget()

    def on_novel_title_selection(self, _e):
        novel_title = self.novel_selector.get()
        if novel_title:
            self.chapter_selector.set_options(get_novel_chapter_titles(novel_title))
        else:
            self.chapter_selector.delete_all()

    def on_chapter_title_selection(self, _e):
        # TODO: use editing chapters
        novel_title = self.novel_selector.get()
        chapter_title = self.chapter_selector.get()
        if novel_title and chapter_title:
            self.chapter_text.set(get_chapter_text(novel_title, chapter_title))

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

        ttk.Button(edit_options_frame, text='[PH] Button 1').grid(
            row=0, column=0, padx=5, pady=5)
        ttk.Button(edit_options_frame, text='[PH] Button 2').grid(
            row=1, column=0, padx=5, pady=5)

        dropdown_frame = ttk.Frame(edit_options_frame)
        dropdown_frame.grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Combobox(dropdown_frame, values=['[PH] Word Suggestion', "Option 1", "Option 2", "Option 3"]).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Button(dropdown_frame, text='[PH] Button 3').pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False)

        entry_frame = ttk.Frame(edit_options_frame)
        entry_frame.grid(
            row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Entry(entry_frame).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Button(entry_frame, text='[PH] Button 4').pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False)


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
