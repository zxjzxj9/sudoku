# Sudoku

A beautiful terminal-based Sudoku game built with Python and [Textual](https://textual.textualize.io/).

![Sudoku Game](https://img.shields.io/badge/terminal-game-4ecdc4?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square)

## Features

- **4 Difficulty Levels** - Easy, Medium, Hard, Expert
- **Mouse & Keyboard Support** - Play your way
- **Smart Highlighting** - Same digits highlighted in teal, conflicts shown in red
- **Digit Counts** - Track progress with X/9 counters for each digit
- **Timer & Best Times** - Race against your personal records
- **Undo/Redo** - Full move history
- **Notes Mode** - Pencil marks for candidates
- **Hints** - Get unstuck when needed

## Installation

```bash
# Clone the repository
git clone https://github.com/zxjzxj9/sudoku.git
cd sudoku

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Controls

### Keyboard

| Key | Action |
|-----|--------|
| `↑ ↓ ← →` | Move selection |
| `1-9` | Enter digit |
| `0` / `Delete` / `Backspace` | Clear cell |
| `N` | Toggle notes mode |
| `U` / `Ctrl+Z` | Undo |
| `R` / `Ctrl+Y` | Redo |
| `H` | Hint |
| `Tab` | Next empty cell |
| `Shift+Tab` | Previous empty cell |
| `Ctrl+N` | New game |
| `Escape` | Deselect |
| `Q` | Quit |

### Mouse

- **Click cell** - Select it
- **Click numpad** - Enter digit
- **Click buttons** - New Game, Undo, Redo, Hint, Notes toggle
- **Click digit count** - Highlight all cells with that digit

## Screenshots

```
╭──────────────────────────────────────────────────────────╮
│  SUDOKU                          ⏱ 03:42  ⭐ Best: 02:15 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│    ┌───┬───┬───┬───┬───┬───┬───┬───┬───┐                │
│    │ 5 │ 3 │   │   │ 7 │   │   │   │   │   ① 8/9       │
│    ├───┼───┼───┼───┼───┼───┼───┼───┼───┤   ② 9/9 ✓     │
│    │ 6 │   │   │ 1 │ 9 │ 5 │   │   │   │   ③ 7/9       │
│    ├───┼───┼───┼───┼───┼───┼───┼───┼───┤   ...         │
│    │   │ 9 │ 8 │   │   │   │   │ 6 │   │                │
│    └───┴───┴───┴───┴───┴───┴───┴───┴───┘   [1][2][3]    │
│                                            [4][5][6]    │
│    [New] [Undo] [Redo] [Hint] [Notes: OFF] [7][8][9]    │
╰──────────────────────────────────────────────────────────╯
```

## Project Structure

```
sudoku/
├── main.py              # Entry point
├── app.py               # Main Textual application
├── requirements.txt     # Dependencies
├── models/
│   ├── board.py         # Board state & validation
│   ├── generator.py     # Puzzle generation algorithm
│   └── game.py          # Game state management
├── widgets/
│   ├── cell.py          # Individual cell widget
│   ├── grid.py          # 9x9 grid widget
│   ├── numpad.py        # Number pad
│   ├── controls.py      # Control buttons
│   └── stats.py         # Timer & digit counts
└── utils/
    ├── storage.py       # Best times persistence
    └── themes.py        # Color definitions
```

## How It Works

### Puzzle Generation

1. Generate a complete valid Sudoku solution using backtracking with randomization
2. Remove cells based on difficulty level while ensuring unique solution
3. Difficulty determines clue count: Easy (36-40), Medium (28-35), Hard (22-27), Expert (17-21)

### Highlighting

- **Selected cell**: Cyan border
- **Same digits**: Teal background
- **Conflicts**: Red background and text
- **Given clues**: White bold text
- **Player entries**: Cyan text

## License

MIT License
