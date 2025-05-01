import tkinter as tk
from tkinter import ttk


class ScrollableListBox(ttk.Frame):
    def __init__(self, *args, display_rows, width=30, text_options=None, **kwargs):
        super().__init__(*args, **kwargs)

        if text_options is None:
            text_options = []

        # Create Listbox
        self.listbox = tk.Listbox(self, height=display_rows, width=width, selectmode=tk.SINGLE)
        self.set_options(text_options)
        self.listbox.pack(side="left", fill="both", expand=True)

        # Create Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")

        # Attach scrollbar to the listbox
        self.listbox.config(yscrollcommand=scrollbar.set)

    def delete_all(self):
        self.listbox.delete(0, tk.END)

    def set_options(self, text_options):
        self.delete_all()
        for item in text_options:
            self.listbox.insert(tk.END, item)

    def get(self):
        selection = self.listbox.curselection()
        if selection:
            return self.listbox.get(selection[0])


class ScrollableTextBox(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.textbox = tk.Text(self, height=5, wrap="word")
        self.textbox.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.textbox.tag_configure("spacing", spacing2=2, spacing3=8)
        self.textbox.tag_add("spacing", "1.0", "end")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.textbox.yview)
        scrollbar.pack(
            side=tk.LEFT, fill=tk.Y, expand=False)

        self.textbox.config(yscrollcommand=scrollbar.set)

    def get(self):
        return self.textbox.get("1.0", "end-1c")

    def set(self, text):
        self.clear()
        self.insert("1.0", text)

    def insert(self, index, text):
        """
        Index	        Meaning
        "1.0"	        Start of the text widget (line 1, char 0)
        "end"	        The very end (after the last character)
        "end-1c"	    One character before the end (removes newline)
        "2.5"	        Line 2, character 5
        "insert"	    Current insertion cursor position
        "current"	    Mouse pointer position (if inside widget)
        "sel.first"	    Start of selected text
        "sel.last"	    End of selected text
        """
        self.textbox.insert(index, text)

        self.textbox.tag_configure("spacing", spacing2=2, spacing3=8)
        self.textbox.tag_add("spacing", "1.0", "end")

    def delete(self, start_index, end_index):
        self.textbox.delete(start_index, end_index)

    def clear(self):
        self.delete("1.0", "end")
