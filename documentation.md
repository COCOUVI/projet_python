###
core/csv_handler.py
Résumé : Ce fichier fournit des fonctions pour manipuler les fichiers CSV. Il inclut des fonctions pour lire, écrire et fusionner des fichiers CSV.
lire_csv : Lit un fichier CSV avec un délimiteur spécifié et retourne les données sous forme de liste de listes. Il gère également les erreurs de fichier non trouvé et autres erreurs de lecture.
on_delimiter_change: Met à jour l'affichage du tableau lors d'un changement de délimiteur.
ecrire_csv : Écrit des données dans un fichier CSV avec un délimiteur spécifié, en gérant les erreurs d'écriture.
fusionner_csv: Fusionne plusieurs fichiers CSV en un seul ensemble de données, en vérifiant que les en-têtes sont identiques.
But : Il encapsule la logique de gestion des fichiers CSV, ce qui permet de séparer la logique de l'interface utilisateur de la logique de gestion des données.

#####

core/undo_redo.py
Résumé : Ce fichier implémente une classe UndoRedoManager pour gérer les opérations d'annulation et de rétablissement (undo/redo).
UndoRedoManager: Initialise les piles d'annulation et de rétablissement.
record_change: Enregistre une modification dans la pile d'annulation et vide la pile de rétablissement.
undo: Annule la dernière modification et la déplace vers la pile de rétablissement.
redo: Rétablit la dernière modification annulée et la déplace vers la pile d'annulation.
But : Il fournit une fonctionnalité d'annulation et de rétablissement générique qui peut être utilisée pour suivre les modifications apportées aux données dans l'interface utilisateur.

####

gui/main_window.py

Résumé : Ce fichier définit la classe MainWindow, qui est la fenêtre principale de l'application. Elle configure l'interface utilisateur en créant et en disposant les composants tels que TableView et MenuBar.
MainWindow: Initialise la fenêtre principale, crée les cadres (frames) pour la disposition des composants, et instancie TableView et MenuBar.
update_table: Met à jour les données affichées dans la TableView.
But : Il sert de point d'entrée pour l'interface utilisateur, en coordonnant les autres composants de l'interface graphique.

####

gui/menu_bar.py

Résumé : Ce fichier définit la classe MenuBar, qui crée la barre de menu de l'application. Cette barre de menu contient les boutons de navigation et les autres commandes de l'application.
MenuBar: Initialise la barre de menu, crée les boutons et leurs fonctions de rappel.
Fonctions de navigation (premiere_ligne, ligne_precedente, etc.): Mettent à jour la vue de la TableView en fonction de la navigation de l'utilisateur.
set_active_entry: Définit l'entrée active et déplace le curseur.
update_table_view: Actualise l'affichage de la TableView et les labels de position.
But : Il fournit les outils de navigation et les commandes de l'application à l'utilisateur.


####

gui/table_view.py

Résumé : Ce fichier définit la classe TableView, qui crée et gère le tableau interactif pour afficher et éditer les données CSV.
TableView: Initialise le tableau, crée les entrées, les en-têtes, les boutons d'annulation et de rétablissement, et gère la sélection et la fusion des cellules.
select_cell et select_cells: Gèrent la sélection des cellules.
merge_selected_cells: Fusionne les cellules sélectionnées.
on_cell_change: Gère les modifications des cellules et les enregistre pour l'annulation et le rétablissement.
undo et redo: Gèrent les opérations d'annulation et de rétablissement.
update_entries_from_df: Met à jour les entrées du tableau à partir du DataFrame.
Fonctions de déplacement des colonnes et des lignes (start_col_drag, on_col_drag, etc.): Gèrent le déplacement interactif des colonnes et des lignes.
afficher_donnees_fusionnees: Affiche les données fusionnées dans la table.
But : Il fournit l'interface principale pour l'affichage et l'édition des données CSV, en incluant des fonctionnalités avancées telles que la sélection, la fusion, l'annulation et le rétablissement des cellules, ainsi que le déplacement des colonnes et des lignes.


####
main.py : Ce fichier est le point d'entrée de l'application, lançant l'interface graphique en créant une instance de la fenêtre principale et en démarrant la boucle d'événements.
