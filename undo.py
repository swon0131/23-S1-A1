from __future__ import annotations
from action import PaintAction
from grid import Grid
from data_structures.stack_adt import ArrayStack

class UndoTracker:

    def __init__(self):
        self.undoArr = ArrayStack(10000)
        self.redoArr = ArrayStack(10000)

    def add_action(self, action: PaintAction) -> None:
        """
        Adds an action to the undo tracker.

        If your collection is already full,
        feel free to exit early and not add the action.
        :complexity:
        Best & Worse Case: O(1) constant time
        """
        if not self.undoArr.is_full():
            self.undoArr.push(action)

    def undo(self, grid: Grid) -> PaintAction|None:
        """
        Undo an operation, and apply the relevant action to the grid.
        If there are no actions to undo, simply do nothing.
        :complexity:
        Best & Worse Case: O(1) constant time
        :return: The action that was undone, or None.
        """
        if not self.undoArr.is_empty():
            popped_action = self.undoArr.pop()
            self.redoArr.push(popped_action)
            popped_action.undo_apply(grid)
            return popped_action
        else:
            return None

    def redo(self, grid: Grid) -> PaintAction|None:
        """
        Redo an operation that was previously undone.
        If there are no actions to redo, simply do nothing.
        :complexity:
        Best & Worse Case: O(1) constant time
        :return: The action that was redone, or None.
        """
        if not self.redoArr.is_empty():
            popped_action = self.redoArr.pop()
            self.undoArr.push(popped_action)
            popped_action.redo_apply(grid)
            return popped_action
        else:
            return None

