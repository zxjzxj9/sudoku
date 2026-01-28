"""Individual Sudoku cell widget."""

from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text


class Cell(Widget):
    """A single cell in the Sudoku grid."""

    DEFAULT_CSS = """
    Cell {
        width: 7;
        height: 3;
        content-align: center middle;
        text-align: center;
        border: solid #333333;
    }

    Cell.given {
        color: #ffffff;
        text-style: bold;
    }

    Cell.player {
        color: #4ecdc4;
    }

    Cell.selected {
        background: #2a4a5a;
        border: solid #4ecdc4;
    }

    Cell.highlighted {
        background: #1a3a3a;
    }

    Cell.conflict {
        color: #ff6b6b;
        background: #3a1a1a;
    }

    Cell:hover {
        background: #252545;
    }

    Cell.box-right {
        border-right: solid #888888;
    }

    Cell.box-bottom {
        border-bottom: solid #888888;
    }
    """

    value: reactive[int] = reactive(0)
    notes: reactive[frozenset] = reactive(frozenset())
    is_given: reactive[bool] = reactive(False)
    is_selected: reactive[bool] = reactive(False)
    is_highlighted: reactive[bool] = reactive(False)
    is_conflict: reactive[bool] = reactive(False)

    class Selected(Message):
        """Message sent when cell is clicked."""
        def __init__(self, row: int, col: int) -> None:
            self.row = row
            self.col = col
            super().__init__()

    def __init__(self, row: int, col: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        self.can_focus = False

    def on_mount(self) -> None:
        """Set up border classes based on position."""
        # Add thick border after 3rd and 6th columns
        if self.col in (2, 5):
            self.add_class("box-right")
        # Add thick border after 3rd and 6th rows
        if self.row in (2, 5):
            self.add_class("box-bottom")

    def on_click(self) -> None:
        """Handle cell click."""
        self.post_message(self.Selected(self.row, self.col))

    def watch_value(self, value: int) -> None:
        """React to value changes."""
        self._update_classes()
        self.refresh()

    def watch_is_given(self, is_given: bool) -> None:
        """React to is_given changes."""
        self._update_classes()

    def watch_is_selected(self, is_selected: bool) -> None:
        """React to selection changes."""
        self._update_classes()

    def watch_is_highlighted(self, is_highlighted: bool) -> None:
        """React to highlight changes."""
        self._update_classes()

    def watch_is_conflict(self, is_conflict: bool) -> None:
        """React to conflict changes."""
        self._update_classes()

    def watch_notes(self, notes: frozenset) -> None:
        """React to notes changes."""
        self.refresh()

    def _update_classes(self) -> None:
        """Update CSS classes based on state."""
        self.remove_class("given", "player", "selected", "highlighted", "conflict")

        if self.is_selected:
            self.add_class("selected")
        elif self.is_conflict:
            self.add_class("conflict")
        elif self.is_highlighted:
            self.add_class("highlighted")

        if self.is_given:
            self.add_class("given")
        elif self.value != 0:
            self.add_class("player")

    def render(self) -> Text:
        """Render the cell content."""
        if self.value != 0:
            return Text(f" {self.value} ", justify="center")
        elif self.notes:
            # Render notes in a compact format
            notes_str = self._format_notes()
            return Text(notes_str, style="dim", justify="center")
        else:
            return Text(" ", justify="center")

    def _format_notes(self) -> str:
        """Format notes as a compact string."""
        sorted_notes = sorted(self.notes)
        if len(sorted_notes) <= 5:
            return " ".join(str(n) for n in sorted_notes)
        else:
            return " ".join(str(n) for n in sorted_notes[:4]) + "+"
