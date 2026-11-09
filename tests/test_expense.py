"""Unit tests for the Expense data model and its validation logic."""

from __future__ import annotations

import pytest

from expense_tracker.expense import Expense


class TestExpenseModel:
    """Test suite for the Expense dataclass and field validations."""

    def test_valid_expense_creation(self) -> None:
        """Verify normal creation with explicit and auto-generated IDs."""
        exp = Expense(
            amount=45.50,
            category="groceries",
            description="Weekly grocery shopping",
            date="2026-11-09",
        )
        assert exp.amount == 45.50
        assert exp.category == "Groceries"  # Capitalized / title-cased
        assert exp.description == "Weekly grocery shopping"
        assert exp.date == "2026-11-09"
        assert isinstance(exp.id, str)
        assert len(exp.id) == 8

    def test_explicit_id_preserved(self) -> None:
        """Verify that passing an explicit ID is honored."""
        exp = Expense(
            id="exp-1234",
            amount=10.00,
            category="Coffee",
            description="Espresso",
            date="2026-11-09",
        )
        assert exp.id == "exp-1234"

    def test_amount_rounding(self) -> None:
        """Verify that floating point amounts are rounded to 2 decimal places."""
        exp = Expense(
            amount=19.956,
            category="Books",
            description="Python book",
            date="2026-11-09",
        )
        assert exp.amount == 19.96

    def test_invalid_amount_zero_or_negative(self) -> None:
        """Verify that zero and negative amounts raise ValueError."""
        with pytest.raises(ValueError, match="strictly greater than 0"):
            Expense(amount=0.0, category="Food", description="Free lunch", date="2026-11-09")

        with pytest.raises(ValueError, match="strictly greater than 0"):
            Expense(amount=-15.0, category="Food", description="Refund?", date="2026-11-09")

    def test_invalid_amount_non_numeric(self) -> None:
        """Verify that non-numeric amounts raise TypeError."""
        with pytest.raises(TypeError, match="Amount must be a numeric value"):
            Expense(amount="twenty", category="Food", description="Lunch", date="2026-11-09")  # type: ignore

    def test_empty_or_blank_category(self) -> None:
        """Verify that empty strings or whitespace-only categories raise ValueError."""
        with pytest.raises(ValueError, match="Category must be a non-empty string"):
            Expense(amount=10.0, category="", description="Lunch", date="2026-11-09")

        with pytest.raises(ValueError, match="Category must be a non-empty string"):
            Expense(amount=10.0, category="   ", description="Lunch", date="2026-11-09")

    def test_empty_or_blank_description(self) -> None:
        """Verify that empty strings or whitespace-only descriptions raise ValueError."""
        with pytest.raises(ValueError, match="Description must be a non-empty string"):
            Expense(amount=10.0, category="Food", description="", date="2026-11-09")

        with pytest.raises(ValueError, match="Description must be a non-empty string"):
            Expense(amount=10.0, category="Food", description="   ", date="2026-11-09")

    def test_invalid_date_formats(self) -> None:
        """Verify that non-ISO-8601 date strings raise ValueError."""
        invalid_dates = [
            "09-11-2026",
            "2026/11/09",
            "2026-13-01",  # Invalid month
            "2026-02-30",  # Invalid day for February
            "yesterday",
            "",
            "   ",
        ]
        for bad_date in invalid_dates:
            with pytest.raises(ValueError):
                Expense(amount=10.0, category="Food", description="Snack", date=bad_date)

    def test_empty_id(self) -> None:
        """Verify that an empty ID string raises ValueError."""
        with pytest.raises(ValueError, match="Expense ID must be a non-empty string"):
            Expense(id="   ", amount=10.0, category="Food", description="Lunch", date="2026-11-09")

    def test_serialization_to_dict(self) -> None:
        """Verify dictionary serialization preserves all fields."""
        exp = Expense(
            id="test-id-1",
            amount=99.99,
            category="Gadgets",
            description="Wireless Mouse",
            date="2026-11-09",
        )
        data = exp.to_dict()
        assert data == {
            "id": "test-id-1",
            "amount": 99.99,
            "category": "Gadgets",
            "description": "Wireless Mouse",
            "date": "2026-11-09",
        }

    def test_deserialization_from_dict(self) -> None:
        """Verify instantiation from dictionary data."""
        raw = {
            "id": "test-id-2",
            "amount": 12.50,
            "category": "Snacks",
            "description": "Protein Bar",
            "date": "2026-11-09",
        }
        exp = Expense.from_dict(raw)
        assert exp.id == "test-id-2"
        assert exp.amount == 12.50
        assert exp.category == "Snacks"
        assert exp.description == "Protein Bar"
        assert exp.date == "2026-11-09"

    def test_from_dict_missing_fields(self) -> None:
        """Verify KeyError is raised when required keys are missing."""
        incomplete = {
            "amount": 12.50,
            "category": "Snacks",
            # missing id, description, date
        }
        with pytest.raises(KeyError, match="Missing required fields"):
            Expense.from_dict(incomplete)

    def test_from_dict_invalid_type(self) -> None:
        """Verify TypeError when from_dict is called with non-dict."""
        with pytest.raises(TypeError, match="Expected dict"):
            Expense.from_dict(["not", "a", "dict"])  # type: ignore

