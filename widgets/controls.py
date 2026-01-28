"""Game control buttons widget."""

from textual.widget import Widget
from textual.widgets import Button
from textual.containers import Horizontal
from textual.message import Message

from models.generator import Difficulty


class Controls(Widget):
    """Game control buttons: New Game, Undo, Redo, Hint, Notes toggle."""

    DEFAULT_CSS = """
    Controls {
        width: 100%;
        height: 5;
        background: #16213e;
        border: round #444444;
    }

    Controls > Horizontal {
        width: 100%;
        height: 100%;
        align: center middle;
        padding: 0 1;
    }

    Controls Button {
        margin: 0 1;
        min-width: 10;
        width: auto;
        height: 3;
        padding: 0 2;
        background: #1a1a2e;
        border: tall #444444;
        color: #4ecdc4;
        content-align: center middle;
    }

    Controls Button:hover {
        background: #2a4a5a;
        border: tall #4ecdc4;
    }

    Controls Button:focus {
        background: #2a4a5a;
    }

    Controls Button.notes-on {
        background: #1a3a3a;
        border: tall #4ecdc4;
        color: #4ecdc4;
    }

    Controls #difficulty-btn {
        min-width: 12;
        color: #ffd700;
        border: tall #ffd70060;
    }

    Controls #difficulty-btn:hover {
        border: tall #ffd700;
        background: #3a3a1a;
    }
    """

    class NewGame(Message):
        """Message for new game request."""
        def __init__(self, difficulty: Difficulty) -> None:
            self.difficulty = difficulty
            super().__init__()

    class Undo(Message):
        """Message for undo request."""
        pass

    class Redo(Message):
        """Message for redo request."""
        pass

    class Hint(Message):
        """Message for hint request."""
        pass

    class ToggleNotes(Message):
        """Message for notes toggle."""
        pass

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.notes_btn: Button | None = None
        self.difficulty_btn: Button | None = None
        self.current_difficulty = Difficulty.MEDIUM
        self._difficulties = list(Difficulty)

    def compose(self):
        """Create control buttons."""
        with Horizontal():
            self.difficulty_btn = Button(
                self.current_difficulty.value.capitalize(),
                id="difficulty-btn"
            )
            yield self.difficulty_btn
            yield Button("New", id="new-btn", variant="primary")
            yield Button("Undo", id="undo-btn")
            yield Button("Redo", id="redo-btn")
            yield Button("Hint", id="hint-btn")
            self.notes_btn = Button("Notes: OFF", id="notes-btn")
            yield self.notes_btn

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "difficulty-btn":
            # Cycle to next difficulty
            idx = self._difficulties.index(self.current_difficulty)
            idx = (idx + 1) % len(self._difficulties)
            self.current_difficulty = self._difficulties[idx]
            if self.difficulty_btn:
                self.difficulty_btn.label = self.current_difficulty.value.capitalize()
        elif btn_id == "new-btn":
            self.post_message(self.NewGame(self.current_difficulty))
        elif btn_id == "undo-btn":
            self.post_message(self.Undo())
        elif btn_id == "redo-btn":
            self.post_message(self.Redo())
        elif btn_id == "hint-btn":
            self.post_message(self.Hint())
        elif btn_id == "notes-btn":
            self.post_message(self.ToggleNotes())

    def update_notes_state(self, notes_on: bool) -> None:
        """Update the notes button state."""
        if self.notes_btn:
            if notes_on:
                self.notes_btn.label = "Notes: ON"
                self.notes_btn.add_class("notes-on")
            else:
                self.notes_btn.label = "Notes: OFF"
                self.notes_btn.remove_class("notes-on")

    def set_difficulty(self, difficulty: Difficulty) -> None:
        """Set the current difficulty display."""
        self.current_difficulty = difficulty
        if self.difficulty_btn:
            self.difficulty_btn.label = difficulty.value.capitalize()
