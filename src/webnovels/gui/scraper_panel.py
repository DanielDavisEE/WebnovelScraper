import tkinter as tk
from tkinter import ttk


class ScraperPanel(ttk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent)

        self.shared_data = shared_data

        self.create_widgets()

    def create_widgets(self):
        pass