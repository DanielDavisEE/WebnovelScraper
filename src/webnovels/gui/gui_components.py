import logging
import tkinter as tk
from tkinter import font, ttk

from webnovels.gui.backend import Backend
from webnovels.utils import WHITESPACE


class ScrollableListBox(ttk.Frame):
    def __init__(self, *args, display_rows, width=30, text_options=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = logging.getLogger(self.__class__.__name__)

        if text_options is None:
            text_options = []

        # Create Listbox
        self.listbox = tk.Listbox(self, height=display_rows, width=width,
                                  selectmode=tk.SINGLE,
                                  exportselection=False,
                                  activestyle='none')
        self.set_options(text_options)
        self.listbox.pack(side="left", fill="both", expand=True)

        # Create Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")

        # Attach scrollbar to the listbox
        self.listbox.config(yscrollcommand=scrollbar.set)

    def delete_all(self):
        self.listbox.delete(0, tk.END)

    def get_options(self):
        return self.listbox.get(0, tk.END)

    def set_options(self, text_options):
        self.delete_all()
        for item in text_options:
            self.listbox.insert(tk.END, item)

    def get(self):
        return self.listbox.curselection()

    def set(self, index):
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(index)
        self.listbox.activate(index)
        self.listbox.see(index)  # Scroll to the item if it's not visible

    def get_value(self):
        selection = self.listbox.curselection()
        if selection:
            return self.listbox.get(selection[0])


class ScrollableTextBox(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = logging.getLogger(self.__class__.__name__)

        self.backend = Backend()

        self.textbox = tk.Text(self, height=5, wrap="word", exportselection=False)
        self.textbox.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.textbox.tag_configure("spacing", spacing2=2, spacing3=8)
        self.textbox.tag_add("spacing", "1.0", "end")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.textbox.yview)
        scrollbar.pack(
            side=tk.LEFT, fill=tk.Y, expand=False)

        self.textbox.config(yscrollcommand=scrollbar.set)

        # Create a red underlined font
        red_underline_font = font.Font(self.textbox, self.textbox.cget("font"))
        red_underline_font.configure(underline=True)

        self.textbox.tag_configure("red_underline", font=red_underline_font, foreground="red")

        self.textbox.bind("<Button-3>", self.on_right_click)
        self.textbox.tag_bind("red_underline", "<Button-3>", self._on_error_right_click)

        self.whitespace = None

    def mark_incorrect(self, start_index: str, end_index: str):
        """ Mark a range of text in red font with an underline

        Args:
            start_index: a Tk style index for the start of the range
            end_index: a Tk style index for the end of the range
        """
        # Insert and apply the tag
        self.textbox.tag_add("red_underline", start_index, end_index)

    def _move_text_cursor_to_event(self, event):
        self.textbox.focus_set()

        # Get the index of the mouse pointer in "line.column" format
        index = self.textbox.index(f"@{event.x},{event.y}")

        # Move the insertion cursor to the click location
        self.textbox.mark_set("insert", index)

        self.backend.selected_error = None

    def on_right_click(self, event):
        self.log.debug("TextWidget right click")
        self._move_text_cursor_to_event(event)

    def _on_error_right_click(self, event):
        self._move_text_cursor_to_event(event)

        cursor_index = self.textbox.index("insert")
        text = self.textbox.get("1.0", "end-1c")
        cursor_pos = self.textbox.count("1.0", cursor_index, "chars")[0]
        self.log.debug(f"{cursor_pos=}")

        # FIXME: can't handle first word being wrong
        tmp_indices = [text.rfind(w, 0, cursor_pos) for w in self.whitespace]
        start_index = max(i for i in tmp_indices if i >= 0)

        tmp_indices = [text.find(w, cursor_pos) for w in self.whitespace] + [len(text)]
        end_index = min(i for i in tmp_indices if i >= 0)

        self.log.info(f"Right clicked error: '{text[start_index + 1:end_index]}' at ({start_index}, {end_index})")

        self.backend.selected_error = start_index + 1, end_index

    def get_selected(self):
        try:
            return self.textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return ""  # Or None

    def get(self):
        return self.textbox.get("1.0", "end-1c")

    def set(self, text):
        self.clear()
        self.insert("1.0", text)
        self.whitespace = [w for w in WHITESPACE if w in text]

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
