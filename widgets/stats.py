"""Stats widget showing timer and digit counts."""

from textual.widget import Widget
from textual.widgets import Static, Label
from textual.containers import Vertical, Horizontal
from textual.message import Message
from rich.text import Text


# Circled number characters for 1-9
CIRCLED_NUMBERS = {
    1: "\u2460", 2: "\u2461", 3: "\u2462",
    4: "\u2463", 5: "\u2464", 6: "\u2465",
    7: "\u2466", 8: "\u2467", 9: "\u2468",
}


class DigitCount(Widget):
    """A single digit count display."""

    DEFAULT_CSS = """
    DigitCount {
        width: 100%;
        height: 1;
        padding: 0 1;
    }

    DigitCount:hover {
        background: #252545;
    }

    DigitCount.complete {
        color: #6bcb77;
    }

    DigitCount.highlighted {
        background: #1a3a3a;
    }
    """

    class Clicked(Message):
        """Message when digit count is clicked."""
        def __init__(self, digit: int) -> None:
            self.digit = digit
            super().__init__()

    def __init__(self, digit: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.digit = digit
        self.count = 0

    def on_click(self) -> None:
        """Handle click."""
        self.post_message(self.Clicked(self.digit))

    def update_count(self, count: int, is_highlighted: bool = False) -> None:
        """Update the count display."""
        self.count = count
        self.remove_class("complete", "highlighted")

        if count >= 9:
            self.add_class("complete")
        elif is_highlighted:
            self.add_class("highlighted")

        self.refresh()

    def render(self) -> Text:
        """Render the digit count."""
        circled = CIRCLED_NUMBERS[self.digit]
        check = " \u2713" if self.count >= 9 else ""
        return Text(f"{circled} {self.count}/9{check}")


class Stats(Widget):
    """Stats panel with timer and digit counts."""

    DEFAULT_CSS = """
    Stats {
        width: 18;
        height: auto;
        background: #16213e;
        border: round #444444;
        padding: 1;
    }

    Stats > Vertical {
        width: 100%;
        height: auto;
    }

    Stats .timer-section {
        width: 100%;
        height: auto;
        padding-bottom: 1;
        border-bottom: solid #444444;
        margin-bottom: 1;
    }

    Stats .timer-label {
        color: #888888;
        text-align: center;
        width: 100%;
    }

    Stats .timer-value {
        color: #4ecdc4;
        text-align: center;
        width: 100%;
        text-style: bold;
    }

    Stats .best-label {
        color: #888888;
        text-align: center;
        width: 100%;
    }

    Stats .best-value {
        color: #ffd700;
        text-align: center;
        width: 100%;
    }

    Stats .counts-label {
        color: #888888;
        text-align: center;
        width: 100%;
        padding-bottom: 1;
    }

    Stats .counts-grid {
        width: 100%;
        height: auto;
    }
    """

    class DigitClicked(Message):
        """Message when a digit count is clicked."""
        def __init__(self, digit: int) -> None:
            self.digit = digit
            super().__init__()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.digit_counts: dict[int, DigitCount] = {}
        self.timer_label: Static | None = None
        self.best_label: Static | None = None

    def compose(self):
        """Create the stats display."""
        with Vertical():
            with Vertical(classes="timer-section"):
                yield Static("\u23f1 Time", classes="timer-label")
                self.timer_label = Static("00:00", classes="timer-value")
                yield self.timer_label
                yield Static("\u2605 Best", classes="best-label")
                self.best_label = Static("--:--", classes="best-value")
                yield self.best_label

            yield Static("Counts", classes="counts-label")
            with Vertical(classes="counts-grid"):
                for digit in range(1, 10):
                    dc = DigitCount(digit, id=f"count-{digit}")
                    self.digit_counts[digit] = dc
                    yield dc

    def on_digit_count_clicked(self, event: DigitCount.Clicked) -> None:
        """Handle digit count click."""
        self.post_message(self.DigitClicked(event.digit))

    def update_timer(self, time_str: str) -> None:
        """Update the timer display."""
        if self.timer_label:
            self.timer_label.update(time_str)

    def update_best_time(self, time_str: str | None) -> None:
        """Update the best time display."""
        if self.best_label:
            self.best_label.update(time_str or "--:--")

    def update_counts(self, counts: dict[int, int], highlighted_digit: int = 0) -> None:
        """Update all digit counts."""
        for digit, dc in self.digit_counts.items():
            dc.update_count(counts.get(digit, 0), digit == highlighted_digit)
