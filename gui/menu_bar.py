import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import core.csv_handler
import csv

class MenuBar(tk.Frame):
    def __init__(self, master, main_window, table_view):
        super().__init__(master)
        self.main_window = main_window
        self.table_view = table_view
        self.current_file = None  # Variable pour stocker le fichier courant

        self.open_button = tk.Button(self, text="Ouvrir", command=self.open_file)
        self.open_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.save_button = tk.Button(self, text="Sauvegarder", command=self.save_file)
        self.save_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.merge_button = tk.Button(self, text="Fusionner CSV", command=self.afficher_apercu_fusion)
        self.merge_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Ajout du menu déroulant pour le délimiteur
        self.delimiter_label = tk.Label(self, text="Délimiteur:")
        self.delimiter_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.delimiter_var = tk.StringVar(self)
        self.delimiter_var.set(',')  # Délimiteur par défaut
        self.delimiter_menu = ttk.Combobox(self, textvariable=self.delimiter_var, values=[',', ';', '\t', '|'])
        self.delimiter_menu.pack(side=tk.LEFT, padx=5, pady=5)
        self.delimiter_menu.bind("<<ComboboxSelected>>", self.on_delimiter_change)  # Ligne manquante ajoutée

        # Barre de navigation
        self.navigation_frame = tk.Frame(self)
        self.navigation_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(self.navigation_frame, text="<<", command=self.premiere_ligne).pack(side=tk.LEFT)
        tk.Button(self.navigation_frame, text="<", command=self.ligne_precedente).pack(side=tk.LEFT)
        self.ligne_label = tk.Label(self.navigation_frame, text="Ligne: 1")
        self.ligne_label.pack(side=tk.LEFT)
        tk.Button(self.navigation_frame, text=">", command=self.ligne_suivante).pack(side=tk.LEFT)
        tk.Button(self.navigation_frame, text=">>", command=self.derniere_ligne).pack(side=tk.LEFT)

        tk.Button(self.navigation_frame, text="Premier Col", command=self.premiere_colonne).pack(side=tk.LEFT)
        tk.Button(self.navigation_frame, text="Col Préc", command=self.colonne_precedente).pack(side=tk.LEFT)
        self.colonne_label = tk.Label(self.navigation_frame, text="Colonne: 1")
        self.colonne_label.pack(side=tk.LEFT)
        tk.Button(self.navigation_frame, text="Col Suiv", command=self.colonne_suivante).pack(side=tk.LEFT)
        tk.Button(self.navigation_frame, text="Dernier Col", command=self.derniere_colonne).pack(side=tk.LEFT)

        self.current_row = 0
        self.current_col = 0
        #activation entry
        self.active_entry = None

    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Fichiers CSV", "*.csv")])
        if filename:
            self.current_file = filename  # Stocke le fichier courant
            delimiter = self.delimiter_var.get()
            data = core.csv_handler.lire_csv(filename, delimiter)
            if data:
                self.main_window.update_table(data)

    def save_file(self):
        if self.current_file:
            # Force la capture des modifications en attente
            current_widget = self.table_view.focus_get()
            if isinstance(current_widget, tk.Entry):
                current_widget.event_generate("<FocusOut>")
            # Sauvegarde les modifications
            self.table_view.sauvegarder_modifications()
            data = self.table_view.get_data()
            delimiter = self.delimiter_var.get()
            core.csv_handler.ecrire_csv(self.current_file, data, delimiter)
        else:
            tk.messagebox.showerror("Erreur", "Aucun fichier ouvert.")

    def afficher_apercu_fusion(self):
        if not self.current_file:
            messagebox.showerror("Erreur", "Veuillez d'abord ouvrir un fichier CSV.")
            return

        fichiers_csv = filedialog.askopenfilenames(filetypes=[("Fichiers CSV", "*.csv")])
        if not fichiers_csv:
            return

        # Ajouter le fichier courant à la liste des fichiers à fusionner
        fichiers_csv = [self.current_file] + list(fichiers_csv)

        delimiter = self.delimiter_var.get()
        entetes = set()
        apercu_donnees = {}

        for fichier in fichiers_csv:
            try:
                with open(fichier, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    ligne1 = next(reader)
                    entetes.add(tuple(ligne1))
                    apercu_donnees[fichier] = [ligne1]

                    for i, ligne in enumerate(reader):
                        if i < 3:
                            apercu_donnees[fichier].append(ligne)
                        elif i == 3:
                            apercu_donnees[fichier].append(["..."])
                            break
            except FileNotFoundError:
                messagebox.showerror("Erreur", f"Fichier non trouvé: {fichier}")
                return
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la lecture de {fichier}: {e}")
                return

        if len(entetes) > 1:
            messagebox.showerror("Erreur", "Les fichiers CSV n'ont pas les mêmes en-têtes.")
            return

        fenetre_apercu = tk.Toplevel(self)
        fenetre_apercu.title("Aperçu de la fusion")

        for fichier, donnees in apercu_donnees.items():
            tk.Label(fenetre_apercu, text=fichier).pack()
            tableau = ttk.Treeview(fenetre_apercu, columns=tuple(range(len(donnees[0]))), show='headings')
            for i, entete in enumerate(donnees[0]):
                tableau.heading(i, text=entete)
            for ligne in donnees[1:]:
                tableau.insert('', 'end', values=ligne)
            tableau.pack()

        tk.Button(fenetre_apercu, text="Confirmer la fusion", command=lambda: self.confirmer_fusion(fichiers_csv, delimiter, fenetre_apercu)).pack()

    def confirmer_fusion(self, fichiers_csv, delimiter, fenetre_apercu):
        try:
            donnees_fusionnees = core.csv_handler.fusionner_csv(fichiers_csv, delimiter)
            if donnees_fusionnees:
                self.table_view.afficher_donnees_fusionnees(donnees_fusionnees)
            fenetre_apercu.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la fusion des fichiers: {e}")

    def on_delimiter_change(self, event):
        if self.current_file:
            delimiter = self.delimiter_var.get()
            data = core.csv_handler.lire_csv(self.current_file, delimiter)
            if data:
                self.main_window.update_table(data)
    
    # Dans menu_bar.py
    def set_active_entry(self):
        """
        Cette fonction définit l'entrée (entry) active dans la TableView, c'est-à-dire l'entrée qui reçoit le focus du curseur.
        Elle est appelée après chaque déplacement dans le tableau pour assurer que le curseur se déplace avec la navigation.
        """
        # Vérifie que les indices de ligne et de colonne sont valides.
        if 0 <= self.current_row < self.table_view.rows and 0 <= self.current_col < self.table_view.cols:
            # Récupère l'entrée correspondante dans la TableView.
            self.active_entry = self.table_view.entries[self.current_row][self.current_col]
            # Déplace le curseur vers cette entrée en lui donnant le focus.
            self.active_entry.focus_set()

    def premiere_ligne(self):
        """
        Cette fonction déplace la vue du tableau à la première ligne du fichier CSV.
        Elle met à jour la variable current_row, puis actualise l'affichage et déplace le curseur.
        """
        self.current_row = 0  # Définit la ligne courante à la première ligne (indice 0).
        self.update_table_view() # Actualise l'affichage de la TableView.
        self.set_active_entry() # Déplace le curseur vers l'entrée correspondante.

    def ligne_precedente(self):
        """
        Cette fonction déplace la vue du tableau à la ligne précédente.
        Elle vérifie d'abord si nous ne sommes pas déjà à la première ligne.
        """
        if self.current_row > 0: # Vérifie si nous ne sommes pas déjà à la première ligne.
            self.current_row -= 1 # Décrémente l'indice de la ligne courante.
            self.update_table_view() # Actualise l'affichage de la TableView.
            self.set_active_entry() # Déplace le curseur vers l'entrée correspondante.

    def ligne_suivante(self):
        """
        Cette fonction déplace la vue du tableau à la ligne suivante.
        Elle vérifie si nous ne sommes pas déjà à la dernière ligne.
        """
        if self.current_row < self.table_view.rows - 1: # Vérifie si nous ne sommes pas à la dernière ligne.
            self.current_row += 1 # Incrémente l'indice de la ligne courante.
            self.update_table_view() # Actualise l'affichage de la TableView.
            self.set_active_entry() # Déplace le curseur vers l'entrée correspondante.

    def derniere_ligne(self):
        """
        Cette fonction déplace la vue du tableau à la dernière ligne du fichier CSV.
        """
        self.current_row = self.table_view.rows - 1 # Définit la ligne courante à la dernière ligne.
        self.update_table_view() # Actualise l'affichage de la TableView.
        self.set_active_entry() # Déplace le curseur vers l'entrée correspondante.

    def premiere_colonne(self):
        """
        Cette fonction déplace la vue du tableau à la première colonne du fichier CSV.
        """
        self.current_col = 0 # Définit la colonne courante à la première colonne (indice 0).
        self.update_table_view() # Actualise l'affichage de la TableView.
        self.set_active_entry() # Déplace le curseur vers l'entrée correspondante.

    def colonne_precedente(self):
        """
        Cette fonction déplace la vue du tableau à la colonne précédente.
        Elle vérifie si nous ne sommes pas déjà à la première colonne.
        """
        if self.current_col > 0: # Vérifie si nous ne sommes pas à la première colonne.
            self.current_col -= 1 # Décrémente l'indice de la colonne courante.
            self.update_table_view() # Actualise l'affichage de la TableView.
            self.set_active_entry() # Déplace le curseur vers l'entrée correspondante.

    def colonne_suivante(self):
        """
        Cette fonction déplace la vue du tableau à la colonne suivante.
        Elle vérifie si nous ne sommes pas déjà à la dernière colonne.
        """
        if self.current_col < self.table_view.cols - 1: # Vérifie si nous ne sommes pas à la dernière colonne.
            self.current_col += 1 # Incrémente l'indice de la colonne courante.
            self.update_table_view() # Actualise l'affichage de la TableView.
            self.set_active_entry() # Déplace le curseur vers l'entrée correspondante.

    def derniere_colonne(self):
        """
        Cette fonction déplace la vue du tableau à la dernière colonne du fichier CSV.
        """
        self.current_col = self.table_view.cols - 1 # Définit la colonne courante à la dernière colonne.
        self.update_table_view() # Actualise l'affichage de la TableView.
        self.set_active_entry() # Déplace le curseur vers l'entrée correspondante.

    def update_table_view(self):
        """
        Cette fonction met à jour l'affichage de la TableView avec les données correspondant à la ligne et à la colonne courantes.
        Elle met également à jour les labels de ligne et de colonne.
        """
        self.table_view.update_entries_from_df(self.current_row, self.current_col) # Met à jour les entrées de la TableView.
        self.ligne_label.config(text=f"Ligne: {self.current_row + 1}") # Met à jour le label de la ligne.
        self.colonne_label.config(text=f"Colonne: {self.current_col + 1}") # Met à jour le label de la colonne. 
    
    