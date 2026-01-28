"""Number pad widget for digit entry."""

from textual.widget import Widget
from textual.widgets import Button, Static
from textual.containers import Container
from textual.message import Message


class Numpad(Widget):
    """A 3x3 number pad plus clear button."""

    DEFAULT_CSS = """
    Numpad {
        width: 24;
        height: 18;
        border: round #444444;
        background: #16213e;
        layout: grid;
        grid-size: 3 4;
        grid-rows: 3 3 3 3;
        grid-gutter: 0;
        padding: 1;
    }

    Numpad Button {
        width: 100%;
        height: 100%;
        min-height: 3;
        background: #1a1a2e;
        border: tall #444444;
        color: #4ecdc4;
        content-align: center middle;
        text-align: center;
    }

    Numpad Button:hover {
        background: #2a4a5a;
        border: tall #4ecdc4;
    }

    Numpad Button:focus {
        background: #2a4a5a;
    }

    Numpad Button.highlighted {
        background: #1a3a3a;
        border: tall #4ecdc4;
    }

    Numpad Button.complete {
        color: #6bcb77;
        border: tall #6bcb77;
    }

    Numpad Button.complete:hover {
        background: #1a3a2a;
    }

    Numpad #clear-btn {
        column-span: 3;
        color: #ff6b6b;
        border: tall #ff6b6b40;
    }

    Numpad #clear-btn:hover {
        background: #3a1a1a;
        border: tall #ff6b6b;
    }
    """

    class DigitPressed(Message):
        """Message when a digit button is pressed."""
        def __init__(self, digit: int) -> None:
            self.digit = digit
            super().__init__()

    class ClearPressed(Message):
        """Message when clear button is pressed."""
        pass

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.digit_buttons: dict[int, Button] = {}

    def compose(self):
        """Create the numpad layout."""
        for digit in range(1, 10):
            btn = Button(str(digit), id=f"num-{digit}")
            self.digit_buttons[digit] = btn
            yield btn
        yield Button("Clear", id="clear-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id
        if btn_id and btn_id.startswith("num-"):
            digit = int(btn_id.split("-")[1])
            self.post_message(self.DigitPressed(digit))
        elif btn_id == "clear-btn":
            self.post_message(self.ClearPressed())

    def update_digit_states(self, counts: dict[int, int], highlighted_digit: int = 0) -> None:
        """Update button states based on digit counts."""
        for digit, btn in self.digit_buttons.items():
            btn.remove_class("complete", "highlighted")

            if counts.get(digit, 0) >= 9:
                btn.add_class("complete")
            elif digit == highlighted_digit:
                btn.add_class("highlighted")
