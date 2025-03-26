# undo_redo.py
class UndoRedoManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def record_change(self, change):
        self.undo_stack.append(change)
        self.redo_stack = []  # Vider redo_stack après une nouvelle modification

    def undo(self):
        if self.undo_stack:
            change = self.undo_stack.pop()
            self.redo_stack.append(change)
            return change
        return None

    def redo(self):
        if self.redo_stack:
            change = self.redo_stack.pop()
            self.undo_stack.append(change)
            return change
        return None