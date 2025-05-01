import tkinter as tk
from tkinter import ttk

from editor_panel import EditorPanel
from scraper_panel import ScraperPanel


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WebNovel Editor")

        self.shared_data = {}

        # Create notebook
        notebook = ttk.Notebook(self)
        notebook.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create and add tab pages
        scraper = ScraperPanel(notebook, shared_data=self.shared_data)
        editor = EditorPanel(notebook, shared_data=self.shared_data)

        notebook.add(scraper, text="Scraping")
        notebook.add(editor, text="Editing")

        # Configure window size and placement
        # self.resizable(False, False)
        self.eval('tk::PlaceWindow . center')
        self.minsize(self.winfo_width(), self.winfo_height())


# Run the app
if __name__ == "__main__":
    app = App()
    app.mainloop()
