"""End-to-end integration test verifying complete CLI workflow through main()."""

from __future__ import annotations

import os
from pathlib import Path
import pytest

from expense_tracker.main import main


def test_full_application_lifecycle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Simulate a complete user session: Add, View, Summary, and Exit."""
    test_db = tmp_path / "integration_expenses.json"
    monkeypatch.setenv("EXPENSE_TRACKER_FILE", str(test_db))

    # Menu sequence:
    # 1. Option '1': Add Expense -> 50.00 -> Food -> Team Lunch -> 2026-11-09
    # 2. Option '2': View All Expenses
    # 3. Option '4': Calculate Total Expenditure
    # 4. Option '6': Category Summary
    # 5. Option '7': Exit
    user_inputs = iter([
        "1", "50.00", "Food", "Team Lunch", "2026-11-09",
        "2",
        "4",
        "6",
        "7"
    ])
    monkeypatch.setattr("builtins.input", lambda *args: next(user_inputs))

    exit_code = main()
    assert exit_code == 0
    assert test_db.exists()

    output = capsys.readouterr().out
    assert "Expense successfully added!" in output
    assert "Team Lunch" in output
    assert "$50.00" in output
    assert "Total Expenditure  : $50.00" in output
    assert "100.0%" in output
    assert "Thank you for using Personal Expense Tracker" in output

