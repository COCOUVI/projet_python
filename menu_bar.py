import tkinter as tk
from tkinter import filedialog
import csv

class MenuBar(tk.Frame):
    def __init__(self, master, main_window, table_view):  # Ajout de table_view
        super().__init__(master)
        self.main_window = main_window
        self.table_view = table_view  # stocke la table view

        self.open_button = tk.Button(self, text="Ouvrir", command=self.open_file)
        self.open_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.save_button = tk.Button(self, text="Sauvegarder", command=self.save_file)
        self.save_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.merge_button = tk.Button(self, text="Fusionner", command=self.merge_files)
        self.merge_button.pack(side=tk.LEFT, padx=10, pady=5)

    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Fichiers CSV", "*.csv")])
        if filename:
            try:
                with open(filename, 'r') as file:
                    reader = csv.reader(file)
                    data = list(reader)
                    self.main_window.update_table(data)
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier : {e}")

    def save_file(self):
        print("Action: Sauvegarder le fichier")

    def merge_files(self):
        self.table_view.merge_selected_cells()  # Appel de la fonction merge_selected_cells de tableview