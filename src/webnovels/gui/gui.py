import tkinter as tk
from tkinter import ttk

from webnovels.gui.editor_panel import EditorPanel
from webnovels.gui.scraper_panel import ScraperPanel


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WebNovel Editor")

        # Create notebook
        notebook = ttk.Notebook(self)
        notebook.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create and add tab pages
        scraper = ScraperPanel(notebook)
        editor = EditorPanel(notebook)

        # notebook.add(scraper, text="Scraping")
        notebook.add(editor, text="Editing")

        # Configure window size and placement
        # self.resizable(False, False)
        self.eval('tk::PlaceWindow . center')
        self.minsize(self.winfo_width(), self.winfo_height())


def main():
    app = App()
    app.mainloop()


# Run the app
if __name__ == "__main__":
    main()
