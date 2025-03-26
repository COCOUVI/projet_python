import tkinter as tk
import pandas as pd
from core.undo_redo import UndoRedoManager 

class TableView(tk.Frame):
    def __init__(self, master=None, rows=10, cols=5):
        super().__init__(master)
        self.master = master
        self.rows = rows
        self.cols = cols
        self.entries = []
        self.df = pd.DataFrame([['' for _ in range(cols)] for _ in range(rows)]) # Utilisation de pandas DataFrame
        self.selected_cells = []
        self.merged_cells = {}
        self.modifications = []  # Ajout : Liste pour stocker les modifications
        self.undo_redo_manager = UndoRedoManager() 
        ######
          # Ajout des boutons Undo et Redo
        self.undo_button = tk.Button(self, text="Undo", command=self.undo)
        self.undo_button.grid(row=self.rows + 1, column=0, columnspan=2)
        self.redo_button = tk.Button(self, text="Redo", command=self.redo)
        self.redo_button.grid(row=self.rows + 1, column=2, columnspan=2)

        self.update_undo_redo_buttons()  # Mettre à jour l'état initial des boutons
            
        #####

        def select_cell(event):
            widget = event.widget
            if isinstance(widget, tk.Entry):  # Vérifier si le widget est un Entry
                row = widget.grid_info()['row'] - 1
                col = widget.grid_info()['column']
                if row >= 0:
                    if (row, col) not in self.selected_cells:
                        self.selected_cells.append((row, col))
                        widget.config(bg='lightblue')  # Changer la couleur de fond
                    else:
                        self.selected_cells.remove((row,col))
                        widget.config(bg='white') # remet la couleur de base

        self.select_cell = select_cell
        for row_entries in self.entries:
            for entry in row_entries:
                entry.bind("<Control-Button-1>", self.select_cell)

        # Création des en-têtes de colonnes
        self.col_headers = [tk.Label(self, text=f"Col {j}", relief=tk.RIDGE) for j in range(cols)]
        for j, header in enumerate(self.col_headers):
            header.grid(row=0, column=j, sticky='nsew')
            header.bind("<ButtonPress-1>", self.start_col_drag)
            header.bind("<B1-Motion>", self.on_col_drag)
            header.bind("<ButtonRelease-1>", self.stop_col_drag)

        # Création des en-têtes de lignes
        self.row_headers = [tk.Label(self, text=f"Row {i}", relief=tk.RIDGE) for i in range(rows)]
        for i, header in enumerate(self.row_headers):
            header.grid(row=i + 1, column=cols, sticky='nsew')
            header.bind("<ButtonPress-1>", self.start_row_drag)
            header.bind("<B1-Motion>", self.on_row_drag)
            header.bind("<ButtonRelease-1>", self.stop_row_drag)

        # Création des cellules
        for i in range(rows):
            row_entries = []
            for j in range(cols):
                entry = tk.Entry(self, width=6)
                entry.grid(row=i + 1, column=j, sticky='nsew')
                entry.bind("<FocusOut>", self.on_cell_change)
                entry.bind("<Return>", self.on_cell_change)
                row_entries.append(entry)
            self.entries.append(row_entries)

        # Configuration du redimensionnement
        for i in range(rows + 1):
            self.grid_rowconfigure(i, weight=1)
        for j in range(cols + 1):
            self.grid_columnconfigure(j, weight=1)

        self.drag_data = {"col": None, "row": None, "x": 0, "y": 0}

        
        def select_cells(event):
            widget = event.widget
            if isinstance(widget, tk.Entry):
                row = widget.grid_info()['row'] - 1
                col = widget.grid_info()['column']
                if row >= 0 and (row, col) not in self.selected_cells:
                    self.selected_cells.append((row, col))
                    widget.config(bg='lightblue') # changer la couleur de fond
                else:
                    self.selected_cells.remove((row,col))
                    widget.config(bg='white')
        self.select_cells = select_cells
        self.bind("<Control-Button-1>", self.select_cell)
        self.bind("<Control-B1-Motion>", self.select_cells)

        def merge_selected_cells():
            if len(self.selected_cells) < 2:
                return

            min_row = min(row for row, col in self.selected_cells)
            max_row = max(row for row, col in self.selected_cells)
            min_col = min(col for row, col in self.selected_cells)
            max_col = max(col for row, col in self.selected_cells)

            if (max_row - min_row + 1) * (max_col - min_col + 1) != len(self.selected_cells):
                return

            merged_text = self.entries[min_row][min_col].get()

            for row, col in self.selected_cells:
                if row == min_row and col == min_col:
                    self.entries[row][col].grid(row=min_row + 1, column=min_col, rowspan=max_row - min_row + 1, columnspan=max_col - min_col + 1, sticky='nsew')
                    self.entries[row][col].delete(0, tk.END)
                    self.entries[row][col].insert(0, merged_text)
                    self.merged_cells[(min_row,min_col)] = (max_row,max_col)
                else:
                    self.entries[row][col].grid_forget()

            for row, col in self.selected_cells:
                self.entries[row][col].config(bg='white')
            self.selected_cells = []

        self.merge_selected_cells = merge_selected_cells

        # self.merge_button = tk.Button(self, text="Fusionner", command=self.merge_selected_cells)
        # self.merge_button.grid(row=rows + 1, column=0, columnspan=cols)

        self.update_entries_from_df() # Mettre à jour les entrées à partir du DataFrame
    #saving modify
    def sauvegarder_modifications(self):
        """Applique les modifications stockées au DataFrame."""
        for modification in self.modifications:
            if modification["type"] == "modification":
                self.df.iloc[modification["ligne"], modification["colonne"]] = modification["nouvelle_valeur"]
        self.modifications = []  # Réinitialiser la liste des modifications
    def get_data(self):
        return self.df.values.tolist() # Retourner les données sous forme de liste

    def set_data(self, data):
        self.df = pd.DataFrame(data)
        self.rows = len(data)
        self.cols = len(data[0]) if data else 0 #ajout de la gestion si data est vide
        self.update_entries_from_df()
    def on_cell_change(self, event):
        widget = event.widget
        row = widget.grid_info()['row'] - 1
        col = widget.grid_info()['column']

        if 0 <= row < self.rows and 0 <= col < self.cols:
            ancienne_valeur = self.df.iloc[row, col]
            nouvelle_valeur = widget.get()

            if ancienne_valeur != nouvelle_valeur:
                self.modifications.append({
                    "type": "modification",
                    "ligne": row,
                    "colonne": col,
                    "ancienne_valeur": ancienne_valeur,
                    "nouvelle_valeur": nouvelle_valeur,
                })
                self.undo_redo_manager.record_change({ # Ajout de record_change
                    "ligne": row,
                    "colonne": col,
                    "ancienne_valeur": ancienne_valeur,
                    "nouvelle_valeur": nouvelle_valeur,
                })
                self.update_undo_redo_buttons()
            else:
                # print("Aucune modification détectée.")
                pass
        else:
            pass
    def update_undo_redo_buttons(self):
        self.undo_button["state"] = tk.NORMAL if self.undo_redo_manager.undo_stack else tk.DISABLED
        self.redo_button["state"] = tk.NORMAL if self.undo_redo_manager.redo_stack else tk.DISABLED

    def undo(self):
        change = self.undo_redo_manager.undo()  # Utilisez la méthode undo
        if change:
            self.df.iloc[change["ligne"], change["colonne"]] = change["ancienne_valeur"]
            self.update_entries_from_df()
            self.update_undo_redo_buttons()
    def redo(self):
        change = self.undo_redo_manager.redo()  # Utilisez la méthode redo
        if change:
            self.df.iloc[change["ligne"], change["colonne"]] = change["nouvelle_valeur"]
            self.update_entries_from_df()
            self.update_undo_redo_buttons()

    def sauvegarder_modifications(self):
        """Applique les modifications stockées au DataFrame."""
        # print(f"Modifications à appliquer : {self.modifications}")  # Debug
        for modification in self.modifications:
            if modification["type"] == "modification":
                self.df.iloc[modification["ligne"], modification["colonne"]] = modification["nouvelle_valeur"]
        self.modifications = []  # Réinitialiser la liste des modifications
    
    def update_entries_from_df(self, current_row=0, current_col=0):
        for i in range(self.rows):
            for j in range(self.cols):
                if i < len(self.entries) and j < len(self.entries[i]):
                    self.entries[i][j].delete(0, tk.END)
                    self.entries[i][j].insert(0, str(self.df.iloc[i, j]))
    def start_col_drag(self, event):
        header = event.widget
        col = header.grid_info()["column"]
        self.drag_data["col"] = col
        self.drag_data["x"] = event.x

    def on_col_drag(self, event):
        if self.drag_data["col"] is not None:
            current_col = self.drag_data["col"]
            delta_x = event.x - self.drag_data["x"]
            if abs(delta_x) > 20:
                direction = 1 if delta_x > 0 else -1
                new_col = current_col + direction
                if 0 <= new_col < self.cols:
                    self.swap_cols(current_col, new_col)
                    self.drag_data["col"] = new_col
                    self.drag_data["x"] = event.x

    def stop_col_drag(self, event):
        self.drag_data["col"] = None

    def swap_cols(self, col1, col2):
        cols = list(self.df.columns)
        cols[col1], cols[col2] = cols[col2], cols[col1]
        self.df = self.df[cols]
        for i in range(self.rows):
            self.entries[i][col1].grid(column=col2)
            self.entries[i][col2].grid(column=col1)
            self.entries[i][col1], self.entries[i][col2] = self.entries[i][col2], self.entries[i][col1]
        self.col_headers[col1].grid(column=col2)
        self.col_headers[col2].grid(column=col1)
        self.col_headers[col1], self.col_headers[col2] = self.col_headers[col2], self.col_headers[col1]
        self.update_entries_from_df()
      
    # Déplacement des lignes
    def start_row_drag(self, event):
        header = event.widget
        row = header.grid_info()["row"] - 1
        self.drag_data["row"] = row
        self.drag_data["y"] = event.y

    def on_row_drag(self, event):
        if self.drag_data["row"] is not None:
            current_row = self.drag_data["row"]
            delta_y = event.y - self.drag_data["y"]
            if abs(delta_y) > 10:
                direction = 1 if delta_y > 0 else -1
                new_row = current_row + direction
                if 0 <= new_row < self.rows:
                    self.swap_rows(current_row, new_row)
                    self.drag_data["row"] = new_row
                    self.drag_data["y"] = event.y

    def stop_row_drag(self, event):
        self.drag_data["row"] = None

    def swap_rows(self, row1, row2):
        if 0 <= row1 < self.rows and 0 <= row2 < self.rows:
            # Échange les lignes dans le DataFrame
            self.df.iloc[[row1, row2]] = self.df.iloc[[row2, row1]].values
            # Échange les éléments dans les entrées et les en-têtes
            for j in range(self.cols):
                if 0 <= j < len(self.entries[row1]) and 0 <= j < len(self.entries[row2]): #vérification supplémentaire
                    self.entries[row1][j].grid(row=row2 + 1)
                    self.entries[row2][j].grid(row=row1 + 1)
                    self.entries[row1][j], self.entries[row2][j] = self.entries[row2][j], self.entries[row1][j]
            self.row_headers[row1].grid(row=row2 + 1)
            self.row_headers[row2].grid(row=row1 + 1)
            self.row_headers[row1], self.row_headers[row2] = self.row_headers[row2], self.row_headers[row1]
            self.update_entries_from_df()
        else:
            print("Indices de lignes hors limites dans swap_rows")
    
    def afficher_donnees_fusionnees(self, donnees_fusionnees):
        """Affiche les données fusionnées dans la table."""
        self.df = pd.DataFrame(donnees_fusionnees)
        self.rows = len(donnees_fusionnees)
        self.cols = len(donnees_fusionnees[0]) if donnees_fusionnees else 0
        self.update_entries_from_df()


    # (Le reste de votre code pour les déplacements des colonnes et des lignes)