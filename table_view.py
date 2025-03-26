import tkinter as tk

class TableView(tk.Frame):
    def __init__(self, master=None, rows=10, cols=5):
        super().__init__(master)
        self.master = master
        self.rows = rows
        self.cols = cols
        self.entries = []
        self.table_data = [['' for _ in range(cols)] for _ in range(rows)]
        self.selected_cells = []
        self.merged_cells = {}  # Stocke les cellules fusionnées

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
                entry.bind("<FocusOut>", lambda event, row=i, col=j: self.on_cell_change(event, row, col))
                entry.bind("<Return>", lambda event, row=i, col=j: self.on_cell_change(event, row, col))
                row_entries.append(entry)
            self.entries.append(row_entries)

        # Configuration du redimensionnement
        for i in range(rows + 1):
            self.grid_rowconfigure(i, weight=1)
        for j in range(cols + 1):
            self.grid_columnconfigure(j, weight=1)

        self.drag_data = {"col": None, "row": None, "x": 0, "y": 0}
        # Définition de select_cells avant le bind
        def select_cells(event):
            row = event.widget.grid_info()['row'] - 1
            col = event.widget.grid_info()['column']
            if row >= 0 and (row, col) not in self.selected_cells:
                self.selected_cells.append((row, col))
                event.widget.config(bg='lightblue')

        self.select_cells = select_cells # Liaison de la fonction à l'instance
        self.bind("<Control-Button-1>", self.select_cell)
        self.bind("<Control-B1-Motion>", self.select_cells)
        # Définition de merge_selected_cells avant le bouton
        def merge_selected_cells():
            if len(self.selected_cells) < 2:
                return  # Besoin d'au moins deux cellules pour fusionner

            min_row = min(row for row, col in self.selected_cells)
            max_row = max(row for row, col in self.selected_cells)
            min_col = min(col for row, col in self.selected_cells)
            max_col = max(col for row, col in self.selected_cells)

            # Vérifier si les cellules sélectionnées forment un rectangle
            if (max_row - min_row + 1) * (max_col - min_col + 1) != len(self.selected_cells):
                return  # Les cellules ne forment pas un rectangle

            # Récupérer le texte de la première cellule
            merged_text = self.entries[min_row][min_col].get()

            # Fusionner les cellules
            for row, col in self.selected_cells:
                if row == min_row and col == min_col:
                    self.entries[row][col].grid(row=min_row + 1, column=min_col, rowspan=max_row - min_row + 1, columnspan=max_col - min_col + 1, sticky='nsew')
                    self.entries[row][col].delete(0, tk.END)
                    self.entries[row][col].insert(0, merged_text)
                    self.merged_cells[(min_row,min_col)] = (max_row,max_col)
                else:
                    self.entries[row][col].grid_forget()

            # Réinitialiser la sélection
            for row, col in self.selected_cells:
                self.entries[row][col].config(bg='white')
            self.selected_cells = []

        self.merge_selected_cells = merge_selected_cells # liaison de la fonction a l'instance


        # Bouton de fusion
        self.merge_button = tk.Button(self, text="Fusionner", command=self.merge_selected_cells)
        self.merge_button.grid(row=rows + 1, column=0, columnspan=cols)

    # Gestion des données
    def get_data(self):
        return self.table_data

    def set_data(self, data):
        self.table_data = data
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                if i < self.rows and j < self.cols:
                    self.entries[i][j].delete(0, tk.END)
                    self.entries[i][j].insert(0, value)

    def on_cell_change(self, event, row, col):
        self.table_data[row][col] = event.widget.get()

    # Déplacement des colonnes
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
        for i in range(self.rows):
            self.entries[i][col1].grid(column=col2)
            self.entries[i][col2].grid(column=col1)
            self.entries[i][col1], self.entries[i][col2] = self.entries[i][col2], self.entries[i][col1]
        self.col_headers[col1].grid(column=col2)
        self.col_headers[col2].grid(column=col1)
        self.col_headers[col1], self.col_headers[col2] = self.col_headers[col2], self.col_headers[col1]
        for row in self.table_data:
            row[col1], row[col2] = row[col2], row[col1]

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
        for j in range(self.cols):
            self.entries[row1][j].grid(row=row2 + 1)
            self.entries[row2][j].grid(row=row1 + 1)
            self.entries[row1][j], self.entries[row2][j] = self.entries[row2][j], self.entries[row1][j]
        self.row_headers[row1].grid(row=row2 + 1)
        self.row_headers[row2].grid(row=row1 + 1)
        self.row_headers[row1], self.row_headers[row2] = self.row_headers[row2], self.row_headers[row1]
        self.table_data[row1], self.table_data[row2] = self.table_data[row2], self.table_data[row1]

    def select_cell(self, event):
        row = event.widget.grid_info()['row'] - 1
        col = event.widget.grid_info()['column']
        if row >= 0:
            if (row, col) not in self.selected_cells:
                self.selected_cells.append((row, col))
                event.widget.config(bg='lightblue')