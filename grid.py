from __future__ import annotations

import layer_store
from layer_store import *
from data_structures.referential_array import ArrayR


class Grid:
    DRAW_STYLE_SET = "SET"
    DRAW_STYLE_ADD = "ADD"
    DRAW_STYLE_SEQUENCE = "SEQUENCE"
    DRAW_STYLE_OPTIONS = (
        DRAW_STYLE_SET,
        DRAW_STYLE_ADD,
        DRAW_STYLE_SEQUENCE
    )

    DEFAULT_BRUSH_SIZE = 2
    MAX_BRUSH = 5
    MIN_BRUSH = 0

    def __init__(self, draw_style, x, y) -> None:
        """
        Initialise the grid object.
        - draw_style:
            The style with which colours will be drawn.
            Should be one of DRAW_STYLE_OPTIONS
            This draw style determines the LayerStore used on each grid square.
        - x, y: The dimensions of the grid.

        Should also intialise the brush size to the DEFAULT provided as a class variable.
        """
        self.x = x
        self.y = y
        self.grid = ArrayR(x)
        self.draw_style = draw_style

        for i in range(x):
            self.grid[i] = ArrayR(y)
            for n in range(y):
                if draw_style == self.DRAW_STYLE_SET:
                    self.grid[i][n] = SetLayerStore()
                elif draw_style == self.DRAW_STYLE_ADD:
                    self.grid[i][n] = AdditiveLayerStore()
                elif draw_style == self.DRAW_STYLE_SEQUENCE:
                    self.grid[i][n] = SequenceLayerStore()

        self.brush_size = self.DEFAULT_BRUSH_SIZE

    def __getitem__(self, index):
        return self.grid[index]

    def __setitem__(self, index, val):
        self.grid[index] = val

    def increase_brush_size(self) -> None:
        """
        Increases the size of the brush by 1,
        if the brush size is already MAX_BRUSH,
        then do nothing.
        """
        if self.brush_size < self.MAX_BRUSH:
            self.brush_size += 1

    def decrease_brush_size(self) -> None:
        """
        Decreases the size of the brush by 1,
        if the brush size is already MIN_BRUSH,
        then do nothing.
        """
        if self.brush_size > self.MIN_BRUSH:
            self.brush_size -= 1

    def special(self):
        """
        Activate the special affect on all grid squares.
        """
        for i in range(self.x):
            for n in range(self.y):
                self.grid[i][n].special()


if __name__ == "__main__":
    grid = Grid("SET", 10, 10)
    print(grid[6][9])


