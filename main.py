"""Convenience launcher for the Personal Expense Tracker application.

Allows running `python main.py` directly from the project root.
"""

import sys
from expense_tracker.main import main

if __name__ == "__main__":
    sys.exit(main())

