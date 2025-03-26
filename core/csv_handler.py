import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import core.csv_handler
import os

def lire_csv(filename, delimiter=','):
    """Lit un fichier CSV avec un délimiteur spécifié."""
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=delimiter)
            return list(reader)
    except FileNotFoundError:
        messagebox.showerror("Erreur", f"Fichier non trouvé : {filename}")
        return None
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier : {e}")
        return None
def on_delimiter_change(self, event):
    """Met à jour le tableau lorsque le délimiteur change."""
    if self.current_file:
        delimiter = self.delimiter_var.get()
        try:
            data = core.csv_handler.lire_csv(self.current_file, delimiter)
            if data:
                self.main_window.update_table(data)
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier : {e}")

def ecrire_csv(filename, data, delimiter=','):
    """Écrit des données dans un fichier CSV avec un délimiteur spécifié."""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=delimiter)
            writer.writerows(data)
        messagebox.showinfo("Succès", f"Données enregistrées dans {filename}")
        return True
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'écriture du fichier : {e}")
        return False

def fusionner_csv(fichiers_csv, delimiter=','):
    """Fusionne plusieurs fichiers CSV avec un délimiteur spécifié."""
    donnees_fusionnees = []
    en_tetes = None

    for fichier_csv in fichiers_csv:
        try:
            lignes = core.csv_handler.lire_csv(fichier_csv, delimiter)
            if lignes is None:
                return None
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la lecture de {fichier_csv}: {e}")
            return None

        if en_tetes is None:
            en_tetes = lignes[0]
        else:
            if lignes[0] != en_tetes:
                messagebox.showerror("Erreur", "Les fichiers CSV n'ont pas les mêmes en-têtes.")
                return None
        donnees_fusionnees.extend(lignes[1:])
    return donnees_fusionnees