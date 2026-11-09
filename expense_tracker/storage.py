"""Data persistence layer for the Expense Tracker application.

Handles loading and saving expense records to a JSON file with safe atomic writes,
missing-file tolerance, and corruption protection.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Sequence

from expense_tracker.expense import Expense


class StorageError(Exception):
    """Base exception for all persistence layer errors."""


class CorruptedDataError(StorageError):
    """Raised when the storage file exists but contains invalid or unreadable data."""


class ExpenseStorage:
    """Manages file-based JSON persistence for Expense objects.

    Ensures data durability through atomic writes and safeguards existing data
    against accidental destruction upon corruption.
    """

    def __init__(self, file_path: str | Path) -> None:
        """Initialize the storage manager with a target JSON file path.

        Args:
            file_path (str | Path): Path to the JSON data file.
        """
        self.file_path = Path(file_path).resolve()

    def load(self) -> list[Expense]:
        """Load and deserialize expenses from the JSON file.

        Returns:
            list[Expense]: List of parsed Expense objects. If the file does not
                exist, an empty list is returned.

        Raises:
            CorruptedDataError: If the file exists but contains invalid JSON,
                is not a list, or contains invalid expense records.
            StorageError: If reading the file fails due to an I/O error.
        """
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except json.JSONDecodeError as err:
            raise CorruptedDataError(
                f"Data file '{self.file_path}' contains corrupted or invalid JSON: {err}"
            ) from err
        except OSError as err:
            raise StorageError(f"I/O error while reading '{self.file_path}': {err}") from err

        if not isinstance(raw_data, list):
            raise CorruptedDataError(
                f"Data file '{self.file_path}' is corrupted: Expected root JSON list, got {type(raw_data).__name__}."
            )

        expenses: list[Expense] = []
        for index, item in enumerate(raw_data):
            try:
                expenses.append(Expense.from_dict(item))
            except (ValueError, KeyError, TypeError) as err:
                raise CorruptedDataError(
                    f"Corrupted record at index {index} in '{self.file_path}': {err}"
                ) from err

        return expenses

    def save(self, expenses: Sequence[Expense]) -> None:
        """Persist a collection of expenses to disk atomically.

        Uses a temporary file and atomic file replacement to ensure the target
        file is never left in a partially written or corrupted state.

        Args:
            expenses (Sequence[Expense]): The list of Expense objects to save.

        Raises:
            StorageError: If writing to the file or replacing fails due to an I/O error.
        """
        try:
            # Ensure the parent directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            payload = [exp.to_dict() for exp in expenses]
            temp_path = self.file_path.with_suffix(".tmp")

            # Write to a temporary file first
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            # Atomically replace target file
            temp_path.replace(self.file_path)

        except OSError as err:
            # Clean up temporary file if it was left behind
            if "temp_path" in locals() and temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise StorageError(f"Failed to save expenses to '{self.file_path}': {err}") from err

