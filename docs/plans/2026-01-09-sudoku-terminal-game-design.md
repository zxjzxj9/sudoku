# Terminal Sudoku Game Design

## Overview

A beautiful, feature-rich terminal Sudoku game built with Python and Textual, supporting both mouse and keyboard controls.

## Tech Stack

- Python 3.10+
- `textual` - TUI framework with mouse support
- `rich` - Terminal styling (bundled with textual)

## Architecture

```
sudoku/
├── main.py              # Entry point, launches Textual app
├── app.py               # Main Textual Application class
├── models/
│   ├── board.py         # Sudoku board state, validation logic
│   ├── generator.py     # Puzzle generation algorithm
│   └── game.py          # Game state (timer, history, scores)
├── widgets/
│   ├── grid.py          # The 9x9 Sudoku grid widget
│   ├── cell.py          # Individual cell widget (handles highlighting)
│   ├── numpad.py        # Clickable number pad (1-9 + clear)
│   ├── controls.py      # Buttons: New Game, Hint, Undo/Redo
│   ├── stats.py         # Timer display, digit counts
│   └── difficulty.py    # Difficulty selector modal
└── utils/
    ├── storage.py       # Save/load best times (JSON file)
    └── themes.py        # Color definitions
```

## Board Model

### `models/board.py`
- 9x9 grid stored as 2D list
- Tracks: `initial_values` (given clues, immutable), `current_values` (player entries), `notes` (pencil marks as sets per cell)
- Validation: `is_valid_move(row, col, num)` checks row/column/box conflicts
- `get_conflicts(row, col)` returns conflicting cell positions
- `get_same_digit_positions(num)` returns all cells containing that number
- `is_complete()` checks if puzzle is solved correctly
- `get_digit_counts()` returns `{1: count, 2: count, ...}`

### `models/generator.py`
1. Generate solved board using backtracking with randomization
2. Remove cells based on difficulty:
   - Easy: 36-40 clues remaining
   - Medium: 28-35 clues
   - Hard: 22-27 clues
   - Expert: 17-21 clues
3. After each removal, verify unique solution exists
4. If removal creates multiple solutions, restore and try another cell

## Visual Design

### Color Scheme (Modern Minimal)

| Element | Color |
|---------|-------|
| Background | Dark gray (`#1a1a2e`) |
| Grid lines (inner) | Dim gray (`#444`) |
| Grid lines (3x3 box) | White (`#888`) + thicker border |
| Given clues (fixed) | White, bold |
| Player entries | Cyan (`#4ecdc4`) |
| Selected cell | Bright cyan border + light bg (`#2a4a5a`) |
| Same digit highlight | Soft teal background (`#1a3a3a`) |
| Conflict/invalid | Red text (`#ff6b6b`) + dim red bg |
| Completed digit (9/9) | Green (`#6bcb77`) with checkmark |
| Notes/pencil marks | Dim gray, small text |

### Grid Structure
- Each 3x3 box is a container widget with thick borders (2px)
- Individual cells inside use thin borders (1px)
- Guarantees visual distinction regardless of font

### Layout
```
╭──────────────────────────────────────────────────────────╮
│  SUDOKU                          ⏱ 03:42  ⭐ Best: 02:15 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│    [9x9 GRID]                         [Digit Counts]     │
│    - 3x3 boxes with thick borders     ① 8/9             │
│    - Cells with thin borders          ② 9/9 ✓           │
│    - Color highlighting               ...               │
│                                                          │
│                                       [Numpad]           │
│                                       1  2  3            │
│                                       4  5  6            │
│                                       7  8  9            │
│                                         Clear            │
│                                                          │
│    [New] [Undo] [Redo] [Hint] [Notes: OFF]              │
╰──────────────────────────────────────────────────────────╯
```

## Controls

### Keyboard

| Key | Action |
|-----|--------|
| `↑ ↓ ← →` | Move selection |
| `1-9` | Enter digit (or toggle note if Notes mode on) |
| `0` / `Delete` / `Backspace` | Clear cell |
| `N` | Toggle Notes mode |
| `U` / `Ctrl+Z` | Undo |
| `R` / `Ctrl+Y` | Redo |
| `H` | Hint (reveal one cell) |
| `Space` | Quick-toggle Notes mode |
| `Ctrl+N` | New game (opens difficulty selector) |
| `Tab` | Move to next empty cell |
| `Shift+Tab` | Move to previous empty cell |
| `Enter` | Confirm selection |
| `Escape` | Deselect / Close dialogs |

### Mouse

| Action | Result |
|--------|--------|
| Click cell | Select it (highlights same digits) |
| Click numpad 1-9 | Enter digit in selected cell |
| Click numpad Clear | Clear selected cell |
| Double-click cell | Quick-clear that cell |
| Click digit count | Highlight all cells with that digit |
| Hover over cell | Subtle hover effect |
| Click control buttons | Execute action |

### Hybrid Interaction
- Mouse and keyboard share the same selection state
- Click a cell, then use keyboard to enter digits, or vice versa
- Arrow keys move from wherever you last clicked
- No mode switching needed

## Game State

### `models/game.py`
```python
@dataclass
class GameState:
    board: Board
    difficulty: Difficulty  # Easy | Medium | Hard | Expert
    timer: float  # seconds elapsed
    history: list[Move]  # for undo/redo
    history_index: int
    notes_mode: bool
    is_paused: bool
    is_complete: bool
```

### Move History
- Each action creates `Move(row, col, old_value, new_value, old_notes, new_notes)`
- Undo: restore previous state, decrement index
- Redo: reapply next state, increment index
- New move after undo: truncates future history

### Timer
- Starts when puzzle loads
- Pauses when: app minimized, dialog open, puzzle complete
- Format: `MM:SS` (or `HH:MM:SS` if over an hour)

## Persistence

### `utils/storage.py`
Saves to `~/.sudoku_scores.json`:
```json
{
  "best_times": {
    "easy": 142,
    "medium": 298,
    "hard": 567,
    "expert": null
  }
}
```

- Updates only when completing faster than previous best
- Shows "New Record!" celebration on new best time

## Highlighting Behavior

1. Select a cell with digit (e.g., `5`)
2. All other cells with `5` get teal background highlight
3. If placing a digit would cause conflict, conflicting cells show red
4. Numpad button for selected digit also highlights
5. Completed digits (count = 9) show dimmed in numpad

## Features Summary

| Category | Features |
|----------|----------|
| Core | 9x9 grid, puzzle generation, validation |
| Difficulty | Easy, Medium, Hard, Expert |
| Controls | Full mouse + keyboard hybrid support |
| Highlighting | Same digit (teal), conflicts (red), selected (cyan) |
| Digit Counts | X/9 for each digit, ✓ when complete |
| Timer | MM:SS display, auto-pause, best times |
| Undo/Redo | Full move history |
| Notes | Pencil marks mode |
| Hints | Reveal one correct cell |
| Persistence | Best times saved to JSON |
