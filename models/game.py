"""Game state management including timer, history, and moves."""

from dataclasses import dataclass, field
from typing import Optional
from copy import deepcopy

from models.board import Board
from models.generator import Difficulty, generate_puzzle, get_hint


@dataclass
class Move:
    """Represents a single move for undo/redo."""
    row: int
    col: int
    old_value: int
    new_value: int
    old_notes: set[int] = field(default_factory=set)
    new_notes: set[int] = field(default_factory=set)


class GameState:
    """Manages the complete state of a Sudoku game."""

    def __init__(self):
        self.board: Board = Board()
        self.solution: list[list[int]] = []
        self.difficulty: Difficulty = Difficulty.MEDIUM
        self.timer: float = 0.0
        self.history: list[Move] = []
        self.history_index: int = -1
        self.notes_mode: bool = False
        self.is_paused: bool = False
        self.is_complete: bool = False
        self.selected_cell: Optional[tuple[int, int]] = None

    def new_game(self, difficulty: Difficulty) -> None:
        """Start a new game with the given difficulty."""
        self.difficulty = difficulty
        puzzle, solution = generate_puzzle(difficulty)
        self.solution = solution
        self.board = Board()
        self.board.load_puzzle(puzzle)
        self.timer = 0.0
        self.history = []
        self.history_index = -1
        self.notes_mode = False
        self.is_paused = False
        self.is_complete = False
        self.selected_cell = (0, 0)

    def make_move(self, row: int, col: int, value: int) -> bool:
        """
        Make a move at the given position.
        Returns True if move was made, False if cell is a given clue.
        """
        if self.is_complete or self.board.is_given(row, col):
            return False

        old_value = self.board.get_value(row, col)
        old_notes = self.board.get_notes(row, col)

        if self.notes_mode and value != 0:
            # Toggle note
            self.board.toggle_note(row, col, value)
            new_notes = self.board.get_notes(row, col)
            move = Move(row, col, old_value, old_value, old_notes, new_notes)
        else:
            # Set value
            self.board.set_value(row, col, value)
            new_notes = set()
            move = Move(row, col, old_value, value, old_notes, new_notes)

        # Truncate future history if we're not at the end
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]

        self.history.append(move)
        self.history_index = len(self.history) - 1

        # Check for completion
        if self.board.is_complete():
            self.is_complete = True

        return True

    def undo(self) -> bool:
        """Undo the last move. Returns True if successful."""
        if self.history_index < 0:
            return False

        move = self.history[self.history_index]
        self.board.set_value(move.row, move.col, move.old_value)
        self.board.notes[move.row][move.col] = move.old_notes.copy()
        self.history_index -= 1
        self.is_complete = False
        return True

    def redo(self) -> bool:
        """Redo a previously undone move. Returns True if successful."""
        if self.history_index >= len(self.history) - 1:
            return False

        self.history_index += 1
        move = self.history[self.history_index]
        self.board.set_value(move.row, move.col, move.new_value)
        self.board.notes[move.row][move.col] = move.new_notes.copy()

        if self.board.is_complete():
            self.is_complete = True

        return True

    def get_hint(self) -> Optional[tuple[int, int, int]]:
        """Get a hint. Returns (row, col, value) or None."""
        return get_hint(self.board.current_values, self.solution)

    def apply_hint(self) -> Optional[tuple[int, int, int]]:
        """Apply a hint to the board. Returns the hint applied or None."""
        hint = self.get_hint()
        if hint:
            row, col, value = hint
            # Temporarily disable notes mode to set the value
            old_notes_mode = self.notes_mode
            self.notes_mode = False
            self.make_move(row, col, value)
            self.notes_mode = old_notes_mode
        return hint

    def toggle_notes_mode(self) -> None:
        """Toggle notes mode on/off."""
        self.notes_mode = not self.notes_mode

    def clear_cell(self, row: int, col: int) -> bool:
        """Clear a cell. Returns True if successful."""
        if self.board.is_given(row, col):
            return False

        old_value = self.board.get_value(row, col)
        old_notes = self.board.get_notes(row, col)

        self.board.set_value(row, col, 0)
        self.board.notes[row][col].clear()

        # Only add to history if there was something to clear
        if old_value != 0 or old_notes:
            move = Move(row, col, old_value, 0, old_notes, set())
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            self.history.append(move)
            self.history_index = len(self.history) - 1

        return True

    def select_cell(self, row: int, col: int) -> None:
        """Select a cell."""
        if 0 <= row < 9 and 0 <= col < 9:
            self.selected_cell = (row, col)

    def move_selection(self, dr: int, dc: int) -> None:
        """Move selection by delta."""
        if self.selected_cell is None:
            self.selected_cell = (0, 0)
            return

        row, col = self.selected_cell
        new_row = max(0, min(8, row + dr))
        new_col = max(0, min(8, col + dc))
        self.selected_cell = (new_row, new_col)

    def move_to_next_empty(self, reverse: bool = False) -> None:
        """Move selection to next empty cell."""
        if self.selected_cell is None:
            self.selected_cell = (0, 0)

        empty_cells = self.board.get_empty_cells()
        if not empty_cells:
            return

        if reverse:
            empty_cells.reverse()

        current = self.selected_cell
        # Find next empty cell after current
        for cell in empty_cells:
            if reverse:
                if cell < current:
                    self.selected_cell = cell
                    return
            else:
                if cell > current:
                    self.selected_cell = cell
                    return

        # Wrap around
        self.selected_cell = empty_cells[0]

    def get_selected_digit(self) -> int:
        """Get the digit in the currently selected cell."""
        if self.selected_cell is None:
            return 0
        row, col = self.selected_cell
        return self.board.get_value(row, col)

    def format_time(self) -> str:
        """Format the timer as MM:SS or HH:MM:SS."""
        total_seconds = int(self.timer)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
