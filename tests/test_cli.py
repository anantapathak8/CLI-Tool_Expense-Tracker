"""Unit tests for the CLI user interface methods and user input validation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import pytest

from expense_tracker.cli import ExpenseCLI
from expense_tracker.manager import ExpenseManager
from expense_tracker.storage import ExpenseStorage


class TestExpenseCLI:
    """Test suite for CLI user prompts, menu loops, and handler actions."""

    @pytest.fixture
    def cli(self, tmp_path: Path) -> ExpenseCLI:
        """Provide an ExpenseCLI instance attached to a clean temporary storage."""
        storage = ExpenseStorage(tmp_path / "cli_test.json")
        manager = ExpenseManager(storage)
        return ExpenseCLI(manager)

    def test_prompt_amount_valid_and_invalid(self, cli: ExpenseCLI, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify prompt_amount loops on negative or non-numeric input until valid."""
        # Provide bad inputs ('abc', '-5', '0') followed by a valid input ('24.50')
        inputs = iter(["abc", "-5", "0", "24.50"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        amount = cli.prompt_amount()
        assert amount == 24.50

    def test_prompt_category_validation(self, cli: ExpenseCLI, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify prompt_category loops on empty string and capitalizes output."""
        inputs = iter(["", "   ", "transport"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        cat = cli.prompt_category()
        assert cat == "Transport"

    def test_prompt_description_validation(self, cli: ExpenseCLI, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify prompt_description loops on empty string."""
        inputs = iter(["", "Metro pass"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        desc = cli.prompt_description()
        assert desc == "Metro pass"

    def test_prompt_date_default_to_today(self, cli: ExpenseCLI, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify empty input returns current date."""
        monkeypatch.setattr("builtins.input", lambda _: "")
        date = cli.prompt_date()
        today = datetime.now().strftime("%Y-%m-%d")
        assert date == today

    def test_prompt_date_custom_valid(self, cli: ExpenseCLI, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify valid custom date is returned."""
        inputs = iter(["bad-date", "2026-05-15"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        date = cli.prompt_date()
        assert date == "2026-05-15"

    def test_handle_add_expense(self, cli: ExpenseCLI, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify handle_add_expense prompts and saves a new expense."""
        inputs = iter(["18.75", "Food", "Sandwich & juice", "2026-11-09"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        cli.handle_add_expense()
        captured = capsys.readouterr().out
        assert "Expense successfully added!" in captured
        assert len(cli.manager.expenses) == 1
        assert cli.manager.expenses[0].amount == 18.75

    def test_handle_view_all_empty_and_populated(
        self, cli: ExpenseCLI, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify handle_view_all prints empty message, then table when populated."""
        cli.handle_view_all()
        captured_empty = capsys.readouterr().out
        assert "No records found" in captured_empty

        cli.manager.add_expense(10.0, "Books", "Algorithms textbook", "2026-11-09")
        cli.handle_view_all()
        captured_full = capsys.readouterr().out
        assert "Algorithms textbook" in captured_full
        assert "$10.00" in captured_full

    def test_handle_delete_expense_confirmed(
        self, cli: ExpenseCLI, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify deleting an expense with user confirmation."""
        exp = cli.manager.add_expense(20.0, "Books", "Novel", "2026-11-09")
        assert len(cli.manager.expenses) == 1

        # Provide valid ID and confirm with 'y'
        inputs = iter([exp.id, "y"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        cli.handle_delete_expense()
        captured = capsys.readouterr().out
        assert "Successfully deleted expense" in captured
        assert len(cli.manager.expenses) == 0

    def test_handle_delete_expense_cancelled(
        self, cli: ExpenseCLI, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify cancelling expense deletion preserves the record."""
        exp = cli.manager.add_expense(20.0, "Books", "Novel", "2026-11-09")
        assert len(cli.manager.expenses) == 1

        # Provide valid ID and cancel with 'n'
        inputs = iter([exp.id, "n"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        cli.handle_delete_expense()
        captured = capsys.readouterr().out
        assert "Deletion cancelled" in captured
        assert len(cli.manager.expenses) == 1

    def test_handle_delete_expense_not_found(
        self, cli: ExpenseCLI, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify handling non-existent ID during deletion."""
        inputs = iter(["non-existent-id"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        cli.handle_delete_expense()
        captured = capsys.readouterr().out
        assert "No expense found with ID 'non-existent-id'" in captured

    def test_handle_calculate_total(self, cli: ExpenseCLI, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify calculate total prints transaction count and total."""
        cli.manager.add_expense(15.50, "Food", "Lunch", "2026-11-09")
        cli.manager.add_expense(14.50, "Food", "Dinner", "2026-11-09")

        cli.handle_calculate_total()
        captured = capsys.readouterr().out
        assert "Total Transactions : 2" in captured
        assert "Total Expenditure  : $30.00" in captured

    def test_handle_filter_by_category(
        self, cli: ExpenseCLI, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify filter by category output."""
        cli.manager.add_expense(15.0, "Travel", "Bus pass", "2026-11-09")
        cli.manager.add_expense(30.0, "Food", "Groceries", "2026-11-09")

        # Search for Travel
        inputs = iter(["travel"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        cli.handle_filter_by_category()
        captured = capsys.readouterr().out
        assert "Bus pass" in captured
        assert "Subtotal for Travel: $15.00" in captured

    def test_handle_category_summary(self, cli: ExpenseCLI, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify category summary rendering."""
        cli.manager.add_expense(25.0, "Food", "Groceries", "2026-11-09")
        cli.manager.add_expense(75.0, "Tech", "Headphones", "2026-11-09")

        cli.handle_category_summary()
        captured = capsys.readouterr().out
        assert "Food" in captured
        assert "Tech" in captured
        assert "25.0%" in captured
        assert "75.0%" in captured
        assert "GRAND TOTAL" in captured

    def test_run_exit_option(self, cli: ExpenseCLI, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify option 7 terminates the CLI run loop."""
        monkeypatch.setattr("builtins.input", lambda _: "7")
        cli.run()
        captured = capsys.readouterr().out
        assert "Thank you for using Personal Expense Tracker" in captured

