"""Main Sudoku application."""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static
from textual.binding import Binding
from textual.timer import Timer

from models.game import GameState
from models.generator import Difficulty
from widgets.grid import SudokuGrid
from widgets.numpad import Numpad
from widgets.controls import Controls
from widgets.stats import Stats
from utils.storage import Storage


class SudokuApp(App):
    """A beautiful terminal Sudoku game."""

    TITLE = "Sudoku"
    SUB_TITLE = "Use arrow keys to move, 1-9 to enter digits"

    CSS = """
    Screen {
        background: #1a1a2e;
        layout: vertical;
    }

    #main-container {
        width: 100%;
        height: 1fr;
        padding: 1;
        layout: vertical;
    }

    #game-area {
        width: 100%;
        height: 1fr;
        align: center top;
    }

    #game-row {
        width: auto;
        height: auto;
        align: center middle;
    }

    #grid-container {
        width: auto;
        height: auto;
        margin-right: 2;
    }

    #side-panel {
        width: 20;
        height: auto;
    }

    #controls-row {
        width: 100%;
        height: 5;
        align: center middle;
        dock: bottom;
    }

    Header {
        background: #16213e;
        color: #4ecdc4;
    }

    Footer {
        background: #16213e;
    }

    #completion-banner {
        width: 100%;
        height: 3;
        background: #1a3a2a;
        border: round #6bcb77;
        content-align: center middle;
        text-align: center;
        color: #6bcb77;
        text-style: bold;
        display: none;
    }

    #completion-banner.visible {
        display: block;
    }
    """

    BINDINGS = [
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("left", "move_left", "Left", show=False),
        Binding("right", "move_right", "Right", show=False),
        Binding("1", "digit(1)", "1", show=False),
        Binding("2", "digit(2)", "2", show=False),
        Binding("3", "digit(3)", "3", show=False),
        Binding("4", "digit(4)", "4", show=False),
        Binding("5", "digit(5)", "5", show=False),
        Binding("6", "digit(6)", "6", show=False),
        Binding("7", "digit(7)", "7", show=False),
        Binding("8", "digit(8)", "8", show=False),
        Binding("9", "digit(9)", "9", show=False),
        Binding("0", "clear_cell", "Clear", show=False),
        Binding("delete", "clear_cell", "Clear", show=False),
        Binding("backspace", "clear_cell", "Clear", show=False),
        Binding("n", "toggle_notes", "Notes", show=True),
        Binding("u", "undo", "Undo", show=True),
        Binding("ctrl+z", "undo", "Undo", show=False),
        Binding("r", "redo", "Redo", show=True),
        Binding("ctrl+y", "redo", "Redo", show=False),
        Binding("h", "hint", "Hint", show=True),
        Binding("tab", "next_empty", "Next Empty", show=False),
        Binding("shift+tab", "prev_empty", "Prev Empty", show=False),
        Binding("ctrl+n", "new_game", "New Game", show=True),
        Binding("escape", "deselect", "Deselect", show=False),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.game = GameState()
        self.storage = Storage()
        self.timer: Timer | None = None
        self.grid: SudokuGrid | None = None
        self.numpad: Numpad | None = None
        self.controls: Controls | None = None
        self.stats: Stats | None = None
        self.completion_banner: Static | None = None

    def compose(self) -> ComposeResult:
        """Create the app layout."""
        yield Header()

        with Container(id="main-container"):
            self.completion_banner = Static(
                "\u2728 Congratulations! Puzzle Solved! \u2728",
                id="completion-banner"
            )
            yield self.completion_banner

            with Vertical(id="game-area"):
                with Horizontal(id="game-row"):
                    with Container(id="grid-container"):
                        self.grid = SudokuGrid()
                        yield self.grid

                    with Vertical(id="side-panel"):
                        self.stats = Stats()
                        yield self.stats
                        self.numpad = Numpad()
                        yield self.numpad

                with Container(id="controls-row"):
                    self.controls = Controls()
                    yield self.controls

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the game on mount."""
        # Start a new game
        self.game.new_game(Difficulty.MEDIUM)
        self._update_display()

        # Start the timer
        self.timer = self.set_interval(1.0, self._tick_timer)

        # Update best time display
        self._update_best_time()

    def _tick_timer(self) -> None:
        """Update the timer every second."""
        if not self.game.is_paused and not self.game.is_complete:
            self.game.timer += 1.0
            if self.stats:
                self.stats.update_timer(self.game.format_time())

    def _update_display(self) -> None:
        """Update all display elements."""
        if not self.grid or not self.stats or not self.numpad:
            return

        # Get highlighted digit (from selected cell)
        highlight_digit = self.game.get_selected_digit()

        # Update grid
        self.grid.update_from_board(
            self.game.board,
            self.game.selected_cell,
            highlight_digit
        )

        # Update stats
        counts = self.game.board.get_digit_counts()
        self.stats.update_counts(counts, highlight_digit)
        self.stats.update_timer(self.game.format_time())

        # Update numpad
        self.numpad.update_digit_states(counts, highlight_digit)

        # Update notes button
        if self.controls:
            self.controls.update_notes_state(self.game.notes_mode)

        # Show/hide completion banner
        if self.completion_banner:
            if self.game.is_complete:
                self.completion_banner.add_class("visible")
            else:
                self.completion_banner.remove_class("visible")

    def _update_best_time(self) -> None:
        """Update the best time display."""
        if not self.stats:
            return

        best = self.storage.get_best_time(self.game.difficulty.value)
        if best is not None:
            minutes = int(best) // 60
            seconds = int(best) % 60
            self.stats.update_best_time(f"{minutes:02d}:{seconds:02d}")
        else:
            self.stats.update_best_time(None)

    def _check_completion(self) -> None:
        """Check if puzzle is complete and handle victory."""
        if self.game.is_complete:
            # Check for new record
            is_record = self.storage.set_best_time(
                self.game.difficulty.value,
                self.game.timer
            )
            self._update_best_time()

            if is_record and self.completion_banner:
                self.completion_banner.update(
                    "\u2728 New Record! Puzzle Solved! \u2728"
                )

    # Message handlers
    def on_sudoku_grid_cell_selected(self, event: SudokuGrid.CellSelected) -> None:
        """Handle cell selection from grid."""
        self.game.select_cell(event.row, event.col)
        self._update_display()

    def on_numpad_digit_pressed(self, event: Numpad.DigitPressed) -> None:
        """Handle numpad digit press."""
        if self.game.selected_cell:
            row, col = self.game.selected_cell
            self.game.make_move(row, col, event.digit)
            self._update_display()
            self._check_completion()

    def on_numpad_clear_pressed(self, event: Numpad.ClearPressed) -> None:
        """Handle numpad clear press."""
        if self.game.selected_cell:
            row, col = self.game.selected_cell
            self.game.clear_cell(row, col)
            self._update_display()

    def on_controls_new_game(self, event: Controls.NewGame) -> None:
        """Handle new game request."""
        self.game.new_game(event.difficulty)
        self._update_display()
        self._update_best_time()
        if self.completion_banner:
            self.completion_banner.remove_class("visible")
            self.completion_banner.update(
                "\u2728 Congratulations! Puzzle Solved! \u2728"
            )

    def on_controls_undo(self, event: Controls.Undo) -> None:
        """Handle undo request."""
        self.action_undo()

    def on_controls_redo(self, event: Controls.Redo) -> None:
        """Handle redo request."""
        self.action_redo()

    def on_controls_hint(self, event: Controls.Hint) -> None:
        """Handle hint request."""
        self.action_hint()

    def on_controls_toggle_notes(self, event: Controls.ToggleNotes) -> None:
        """Handle notes toggle."""
        self.action_toggle_notes()

    def on_stats_digit_clicked(self, event: Stats.DigitClicked) -> None:
        """Handle digit count click - highlight all of that digit."""
        # Find first cell with this digit and select it
        positions = self.game.board.get_same_digit_positions(event.digit)
        if positions:
            row, col = positions[0]
            self.game.select_cell(row, col)
            self._update_display()

    # Actions
    def action_move_up(self) -> None:
        """Move selection up."""
        self.game.move_selection(-1, 0)
        self._update_display()

    def action_move_down(self) -> None:
        """Move selection down."""
        self.game.move_selection(1, 0)
        self._update_display()

    def action_move_left(self) -> None:
        """Move selection left."""
        self.game.move_selection(0, -1)
        self._update_display()

    def action_move_right(self) -> None:
        """Move selection right."""
        self.game.move_selection(0, 1)
        self._update_display()

    def action_digit(self, digit: int) -> None:
        """Enter a digit."""
        if self.game.selected_cell:
            row, col = self.game.selected_cell
            self.game.make_move(row, col, digit)
            self._update_display()
            self._check_completion()

    def action_clear_cell(self) -> None:
        """Clear the selected cell."""
        if self.game.selected_cell:
            row, col = self.game.selected_cell
            self.game.clear_cell(row, col)
            self._update_display()

    def action_toggle_notes(self) -> None:
        """Toggle notes mode."""
        self.game.toggle_notes_mode()
        self._update_display()

    def action_undo(self) -> None:
        """Undo last move."""
        self.game.undo()
        self._update_display()

    def action_redo(self) -> None:
        """Redo last undone move."""
        self.game.redo()
        self._update_display()

    def action_hint(self) -> None:
        """Apply a hint."""
        hint = self.game.apply_hint()
        if hint:
            row, col, _ = hint
            self.game.select_cell(row, col)
        self._update_display()
        self._check_completion()

    def action_next_empty(self) -> None:
        """Move to next empty cell."""
        self.game.move_to_next_empty()
        self._update_display()

    def action_prev_empty(self) -> None:
        """Move to previous empty cell."""
        self.game.move_to_next_empty(reverse=True)
        self._update_display()

    def action_new_game(self) -> None:
        """Start a new game with current difficulty."""
        self.game.new_game(self.game.difficulty)
        self._update_display()
        self._update_best_time()
        if self.completion_banner:
            self.completion_banner.remove_class("visible")

    def action_deselect(self) -> None:
        """Deselect current cell."""
        self.game.selected_cell = None
        self._update_display()
