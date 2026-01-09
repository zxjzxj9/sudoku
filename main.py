#!/usr/bin/env python3
"""Entry point for the Sudoku game."""

from app import SudokuApp


def main():
    """Run the Sudoku app."""
    app = SudokuApp()
    app.run()


if __name__ == "__main__":
    main()
