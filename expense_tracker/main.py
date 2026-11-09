"""Main application entry point for the Expense Tracker.

Sets up dependencies (Storage, Manager, CLI) and launches the interactive loop.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

from expense_tracker.cli import ExpenseCLI
from expense_tracker.manager import ExpenseManager
from expense_tracker.storage import CorruptedDataError, ExpenseStorage


def get_default_storage_path() -> Path:
    """Determine the default location for the expenses JSON file.

    Returns:
        Path: Resolved absolute path to 'data/expenses.json'.
    """
    env_path = os.environ.get("EXPENSE_TRACKER_FILE")
    if env_path:
        return Path(env_path).resolve()
    base_dir = Path(__file__).resolve().parent.parent
    return base_dir / "data" / "expenses.json"


def main() -> int:
    """Initialize components and execute the CLI loop.

    Returns:
        int: Process exit code (0 for success, non-zero for fatal error).
    """
    storage_path = get_default_storage_path()
    storage = ExpenseStorage(storage_path)

    try:
        manager = ExpenseManager(storage)
    except CorruptedDataError as err:
        print("\n" + "=" * 65)
        print(" [FATAL ERROR] Corrupted Expense Data File Detected!")
        print("=" * 65)
        print(f"File location: {storage_path}")
        print(f"Details      : {err}")
        print("\nTo prevent permanent loss of your data, the application will not")
        print("overwrite this file automatically.")
        print("Please repair the JSON file manually or rename it before restarting.")
        print("=" * 65 + "\n")
        return 1

    cli = ExpenseCLI(manager)
    cli.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())

