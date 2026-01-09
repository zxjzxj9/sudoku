"""Sudoku puzzle generator with difficulty levels."""

import random
from copy import deepcopy
from enum import Enum


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


# Number of clues to leave based on difficulty
DIFFICULTY_CLUES = {
    Difficulty.EASY: (36, 40),
    Difficulty.MEDIUM: (28, 35),
    Difficulty.HARD: (22, 27),
    Difficulty.EXPERT: (17, 21),
}


def generate_puzzle(difficulty: Difficulty = Difficulty.MEDIUM) -> tuple[list[list[int]], list[list[int]]]:
    """
    Generate a Sudoku puzzle with the given difficulty.
    Returns (puzzle, solution) where puzzle has some cells set to 0.
    """
    # Generate a complete solved board
    solution = _generate_solved_board()

    # Create puzzle by removing cells
    puzzle = _create_puzzle(solution, difficulty)

    return puzzle, solution


def _generate_solved_board() -> list[list[int]]:
    """Generate a completely filled valid Sudoku board."""
    board = [[0] * 9 for _ in range(9)]
    _fill_board(board)
    return board


def _fill_board(board: list[list[int]]) -> bool:
    """Fill the board using backtracking with randomization."""
    # Find next empty cell
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                # Try digits in random order
                digits = list(range(1, 10))
                random.shuffle(digits)

                for digit in digits:
                    if _is_valid(board, row, col, digit):
                        board[row][col] = digit
                        if _fill_board(board):
                            return True
                        board[row][col] = 0

                return False

    return True  # Board is complete


def _is_valid(board: list[list[int]], row: int, col: int, digit: int) -> bool:
    """Check if placing digit at (row, col) is valid."""
    # Check row
    if digit in board[row]:
        return False

    # Check column
    if digit in [board[r][col] for r in range(9)]:
        return False

    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if board[r][c] == digit:
                return False

    return True


def _create_puzzle(solution: list[list[int]], difficulty: Difficulty) -> list[list[int]]:
    """Create a puzzle by removing cells from the solution."""
    puzzle = deepcopy(solution)
    min_clues, max_clues = DIFFICULTY_CLUES[difficulty]
    target_clues = random.randint(min_clues, max_clues)

    # Get all cell positions and shuffle them
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    current_clues = 81
    removed = []

    for row, col in cells:
        if current_clues <= target_clues:
            break

        # Remember the value
        value = puzzle[row][col]
        puzzle[row][col] = 0

        # Check if puzzle still has unique solution
        if _count_solutions(deepcopy(puzzle), limit=2) != 1:
            # Multiple solutions, restore the cell
            puzzle[row][col] = value
        else:
            current_clues -= 1
            removed.append((row, col))

    return puzzle


def _count_solutions(board: list[list[int]], limit: int = 2) -> int:
    """
    Count the number of solutions for a puzzle.
    Stops early if count reaches limit (for efficiency).
    """
    solutions = [0]

    def solve(b: list[list[int]]) -> bool:
        if solutions[0] >= limit:
            return True

        # Find next empty cell
        for row in range(9):
            for col in range(9):
                if b[row][col] == 0:
                    for digit in range(1, 10):
                        if _is_valid(b, row, col, digit):
                            b[row][col] = digit
                            solve(b)
                            b[row][col] = 0

                            if solutions[0] >= limit:
                                return True
                    return False

        # No empty cells - found a solution
        solutions[0] += 1
        return False

    solve(board)
    return solutions[0]


def get_hint(puzzle: list[list[int]], solution: list[list[int]]) -> tuple[int, int, int] | None:
    """
    Get a hint for the puzzle.
    Returns (row, col, value) for one empty or incorrect cell, or None if solved.
    """
    # First check for incorrect cells
    for row in range(9):
        for col in range(9):
            if puzzle[row][col] != 0 and puzzle[row][col] != solution[row][col]:
                return (row, col, solution[row][col])

    # Then find an empty cell
    for row in range(9):
        for col in range(9):
            if puzzle[row][col] == 0:
                return (row, col, solution[row][col])

    return None
