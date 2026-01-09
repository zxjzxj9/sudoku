"""Persistence for best times."""

import json
from pathlib import Path
from typing import Optional


class Storage:
    """Handles saving and loading best times."""

    DEFAULT_PATH = Path.home() / ".sudoku_scores.json"

    def __init__(self, path: Optional[Path] = None):
        self.path = path or self.DEFAULT_PATH
        self._data = self._load()

    def _load(self) -> dict:
        """Load data from file."""
        if self.path.exists():
            try:
                with open(self.path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"best_times": {"easy": None, "medium": None, "hard": None, "expert": None}}

    def _save(self) -> None:
        """Save data to file."""
        try:
            with open(self.path, "w") as f:
                json.dump(self._data, f, indent=2)
        except IOError:
            pass

    def get_best_time(self, difficulty: str) -> Optional[float]:
        """Get best time for a difficulty level."""
        return self._data.get("best_times", {}).get(difficulty.lower())

    def set_best_time(self, difficulty: str, time: float) -> bool:
        """
        Set best time if it's a new record.
        Returns True if it was a new record.
        """
        difficulty = difficulty.lower()
        current_best = self.get_best_time(difficulty)

        if current_best is None or time < current_best:
            if "best_times" not in self._data:
                self._data["best_times"] = {}
            self._data["best_times"][difficulty] = time
            self._save()
            return True
        return False

    def get_all_best_times(self) -> dict:
        """Get all best times."""
        return self._data.get("best_times", {})
