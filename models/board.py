"""Sudoku board model with validation logic."""

from typing import Optional
from copy import deepcopy


class Board:
    """Represents a Sudoku board with validation and state tracking."""

    def __init__(self):
        # 9x9 grid, 0 means empty
        self.initial_values: list[list[int]] = [[0] * 9 for _ in range(9)]
        self.current_values: list[list[int]] = [[0] * 9 for _ in range(9)]
        # Notes: set of candidate digits for each cell
        self.notes: list[list[set[int]]] = [[set() for _ in range(9)] for _ in range(9)]

    def load_puzzle(self, puzzle: list[list[int]]) -> None:
        """Load a puzzle into the board."""
        self.initial_values = deepcopy(puzzle)
        self.current_values = deepcopy(puzzle)
        self.notes = [[set() for _ in range(9)] for _ in range(9)]

    def get_value(self, row: int, col: int) -> int:
        """Get the current value at a position."""
        return self.current_values[row][col]

    def set_value(self, row: int, col: int, value: int) -> bool:
        """
        Set a value at a position.
        Returns False if the cell is a given clue (immutable).
        """
        if self.initial_values[row][col] != 0:
            return False
        self.current_values[row][col] = value
        if value != 0:
            self.notes[row][col].clear()
        return True

    def is_given(self, row: int, col: int) -> bool:
        """Check if a cell contains a given clue."""
        return self.initial_values[row][col] != 0

    def clear_cell(self, row: int, col: int) -> bool:
        """Clear a cell. Returns False if it's a given clue."""
        return self.set_value(row, col, 0)

    def toggle_note(self, row: int, col: int, digit: int) -> bool:
        """Toggle a note digit in a cell. Returns False if cell has a value."""
        if self.current_values[row][col] != 0:
            return False
        if digit in self.notes[row][col]:
            self.notes[row][col].remove(digit)
        else:
            self.notes[row][col].add(digit)
        return True

    def get_notes(self, row: int, col: int) -> set[int]:
        """Get notes for a cell."""
        return self.notes[row][col].copy()

    def is_valid_placement(self, row: int, col: int, value: int) -> bool:
        """Check if placing a value at position would be valid."""
        if value == 0:
            return True

        # Check row
        for c in range(9):
            if c != col and self.current_values[row][c] == value:
                return False

        # Check column
        for r in range(9):
            if r != row and self.current_values[r][col] == value:
                return False

        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r, c) != (row, col) and self.current_values[r][c] == value:
                    return False

        return True

    def get_conflicts(self, row: int, col: int) -> list[tuple[int, int]]:
        """Get list of cells that conflict with the value at given position."""
        conflicts = []
        value = self.current_values[row][col]

        if value == 0:
            return conflicts

        # Check row
        for c in range(9):
            if c != col and self.current_values[row][c] == value:
                conflicts.append((row, c))

        # Check column
        for r in range(9):
            if r != row and self.current_values[r][col] == value:
                conflicts.append((r, col))

        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r, c) != (row, col) and self.current_values[r][c] == value:
                    if (r, c) not in conflicts:
                        conflicts.append((r, c))

        return conflicts

    def get_same_digit_positions(self, digit: int) -> list[tuple[int, int]]:
        """Get all positions containing the given digit."""
        if digit == 0:
            return []
        positions = []
        for r in range(9):
            for c in range(9):
                if self.current_values[r][c] == digit:
                    positions.append((r, c))
        return positions

    def get_digit_counts(self) -> dict[int, int]:
        """Get count of each digit on the board."""
        counts = {i: 0 for i in range(1, 10)}
        for row in self.current_values:
            for val in row:
                if val != 0:
                    counts[val] += 1
        return counts

    def is_complete(self) -> bool:
        """Check if the puzzle is completely and correctly solved."""
        # Check all cells are filled
        for row in self.current_values:
            if 0 in row:
                return False

        # Check all rows
        for row in self.current_values:
            if len(set(row)) != 9:
                return False

        # Check all columns
        for col in range(9):
            column = [self.current_values[row][col] for row in range(9)]
            if len(set(column)) != 9:
                return False

        # Check all 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                box = []
                for r in range(3):
                    for c in range(3):
                        box.append(self.current_values[box_row * 3 + r][box_col * 3 + c])
                if len(set(box)) != 9:
                    return False

        return True

    def get_empty_cells(self) -> list[tuple[int, int]]:
        """Get list of empty cell positions."""
        empty = []
        for r in range(9):
            for c in range(9):
                if self.current_values[r][c] == 0:
                    empty.append((r, c))
        return empty

    def copy(self) -> "Board":
        """Create a deep copy of the board."""
        new_board = Board()
        new_board.initial_values = deepcopy(self.initial_values)
        new_board.current_values = deepcopy(self.current_values)
        new_board.notes = deepcopy(self.notes)
        return new_board
