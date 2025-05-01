import tkinter as tk
from tkinter import ttk
from gui_components import ScrollableListBox, ScrollableTextBox


class EditorPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.novel_selector = None
        self.chapter_selector = None

        self.chapter_text = None

        self.create_selector_widget()
        self.create_editor_widget()


    def create_selector_widget(self):
        chapter_select_frame = ttk.Frame(self)
        chapter_select_frame.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False)

        self.novel_selector = ttk.Combobox(chapter_select_frame, values=['[PH] Novel Name', "Option 1", "Option 2", "Option 3"])
        self.novel_selector.current(0)
        self.novel_selector.state(["readonly"])
        self.novel_selector.pack(
            side=tk.TOP, fill=tk.X, expand=False)

        self.chapter_selector = ScrollableListBox(chapter_select_frame, display_rows=20, text_options=[f'[PH] Chapter {i}' for i in range(1, 41)])
        self.chapter_selector.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True)

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
        self.chapter_text.set("""[PH] It was May 8th, 2020 for the third time, and Ryan had already caused two traffic accidents.
[PH] He blamed the people of New Rome for this. The city’s inhabitants were as nervous as coffee addicts in the morning, and drove their cars like monkeys out for his blood. Moving on the walkway would have been safer.
[PH] Thankfully, he had saved right before passing the <em>‘Welcome to New Rome’</em> sign at the end of the highway linking the city to the rest of the Campania region.""")

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
