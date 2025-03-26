import tkinter as tk
from gui.menu_bar import MenuBar
from gui.table_view import TableView

class MainWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Éditeur CSV")
        self.pack(fill=tk.BOTH, expand=True)

        self.main_frame = tk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=5)

        self.table_view = TableView(self.main_frame, rows=20, cols=6)
        self.table_view.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.menu_bar = MenuBar(self.button_frame, self, self.table_view)  # Passe table_view ici
        self.menu_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def update_table(self, data):
        self.table_view.set_data(data)