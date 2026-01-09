"""Sudoku grid widget containing all cells."""

from textual.widget import Widget
from textual.containers import Container, Grid
from textual.message import Message

from widgets.cell import Cell
from models.board import Board


class SudokuGrid(Widget):
    """The 9x9 Sudoku grid."""

    DEFAULT_CSS = """
    SudokuGrid {
        width: 47;
        height: 29;
        border: round #4ecdc4;
        padding: 0;
        background: #1a1a2e;
    }

    SudokuGrid > Grid {
        grid-size: 9 9;
        grid-gutter: 0;
        padding: 0;
        width: 100%;
        height: 100%;
    }

    SudokuGrid .box-separator-v {
        border-right: thick #888888;
    }

    SudokuGrid .box-separator-h {
        border-bottom: thick #888888;
    }
    """

    class CellSelected(Message):
        """Message when a cell is selected."""
        def __init__(self, row: int, col: int) -> None:
            self.row = row
            self.col = col
            super().__init__()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cells: list[list[Cell]] = []

    def compose(self):
        """Create the grid of cells."""
        with Grid():
            for row in range(9):
                row_cells = []
                for col in range(9):
                    cell = Cell(row, col, id=f"cell-{row}-{col}")
                    row_cells.append(cell)
                    yield cell
                self.cells.append(row_cells)

    def on_cell_selected(self, event: Cell.Selected) -> None:
        """Handle cell selection."""
        self.post_message(self.CellSelected(event.row, event.col))

    def update_from_board(self, board: Board, selected: tuple[int, int] | None,
                          highlight_digit: int = 0) -> None:
        """Update all cells from board state."""
        # Get conflicts for the selected cell
        conflicts = set()
        if selected:
            sel_row, sel_col = selected
            sel_value = board.get_value(sel_row, sel_col)
            if sel_value != 0:
                conflicts = set(board.get_conflicts(sel_row, sel_col))
                # Add the selected cell itself if it has conflicts
                if conflicts:
                    conflicts.add(selected)

        # Get positions of highlighted digit
        highlighted_positions = set()
        if highlight_digit != 0:
            highlighted_positions = set(board.get_same_digit_positions(highlight_digit))

        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                cell.value = board.get_value(row, col)
                cell.notes = frozenset(board.get_notes(row, col))
                cell.is_given = board.is_given(row, col)
                cell.is_selected = selected == (row, col)
                cell.is_highlighted = (row, col) in highlighted_positions and not cell.is_selected
                cell.is_conflict = (row, col) in conflicts

    def get_cell(self, row: int, col: int) -> Cell:
        """Get a cell by position."""
        return self.cells[row][col]
