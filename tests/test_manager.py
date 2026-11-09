"""Unit tests for the ExpenseManager business logic layer."""

from __future__ import annotations

from pathlib import Path
import pytest

from expense_tracker.manager import ExpenseManager
from expense_tracker.storage import ExpenseStorage


class TestExpenseManager:
    """Test suite for the ExpenseManager orchestration class."""

    @pytest.fixture
    def manager(self, tmp_path: Path) -> ExpenseManager:
        """Provide an ExpenseManager instance using an isolated temp directory."""
        storage_file = tmp_path / "test_expenses.json"
        storage = ExpenseStorage(storage_file)
        return ExpenseManager(storage)

    def test_add_expense(self, manager: ExpenseManager) -> None:
        """Verify adding an expense stores it in memory and file."""
        created = manager.add_expense(
            amount=25.00,
            category="Food",
            description="Dinner with friends",
            date="2026-11-09",
        )
        assert created.amount == 25.00
        assert created.category == "Food"
        assert len(manager.expenses) == 1
        assert manager.storage.load()[0].id == created.id

    def test_list_expenses_sorted_by_date(self, manager: ExpenseManager) -> None:
        """Verify that expenses are listed in descending date order by default."""
        manager.add_expense(amount=10.0, category="Food", description="Oldest", date="2026-11-01")
        manager.add_expense(amount=20.0, category="Travel", description="Newest", date="2026-11-09")
        manager.add_expense(amount=15.0, category="Books", description="Middle", date="2026-11-05")

        listed = manager.list_expenses(sort_by_date_desc=True)
        assert [e.date for e in listed] == ["2026-11-09", "2026-11-05", "2026-11-01"]

    def test_get_expense_by_id(self, manager: ExpenseManager) -> None:
        """Verify looking up an expense by ID."""
        exp = manager.add_expense(
            amount=12.0, category="Tech", description="Cable", date="2026-11-09", expense_id="cbl-1"
        )
        found = manager.get_expense_by_id("cbl-1")
        assert found is not None
        assert found.id == exp.id
        assert manager.get_expense_by_id("non-existent") is None

    def test_delete_existing_expense(self, manager: ExpenseManager) -> None:
        """Verify deleting an existing expense removes it from memory and disk."""
        exp1 = manager.add_expense(amount=10.0, category="Food", description="Item 1", date="2026-11-01")
        exp2 = manager.add_expense(amount=20.0, category="Food", description="Item 2", date="2026-11-02")
        assert len(manager.expenses) == 2

        deleted = manager.delete_expense(exp1.id)
        assert deleted.id == exp1.id
        assert len(manager.expenses) == 1
        assert manager.get_expense_by_id(exp1.id) is None

        # Confirm persisted file reflects deletion
        persisted = manager.storage.load()
        assert len(persisted) == 1
        assert persisted[0].id == exp2.id

    def test_delete_non_existent_expense_raises_key_error(self, manager: ExpenseManager) -> None:
        """Verify attempting to delete a missing ID raises KeyError."""
        with pytest.raises(KeyError, match="was not found"):
            manager.delete_expense("unknown-id-xyz")

    def test_calculate_total_empty(self, manager: ExpenseManager) -> None:
        """Verify total calculation on empty manager is 0.0."""
        assert manager.calculate_total() == 0.0

    def test_calculate_total_multiple(self, manager: ExpenseManager) -> None:
        """Verify total calculation sums all items and rounds properly."""
        manager.add_expense(amount=10.25, category="Food", description="Item 1", date="2026-11-01")
        manager.add_expense(amount=20.50, category="Travel", description="Item 2", date="2026-11-02")
        manager.add_expense(amount=5.10, category="Food", description="Item 3", date="2026-11-03")

        assert manager.calculate_total() == 35.85

    def test_filter_by_category(self, manager: ExpenseManager) -> None:
        """Verify case-insensitive filtering by category."""
        manager.add_expense(amount=10.0, category="Food", description="Lunch", date="2026-11-01")
        manager.add_expense(amount=25.0, category="Travel", description="Bus", date="2026-11-02")
        manager.add_expense(amount=15.0, category="food", description="Dinner", date="2026-11-03")

        # Search with lowercase "food"
        food_items = manager.filter_by_category("food")
        assert len(food_items) == 2
        assert all(item.category == "Food" for item in food_items)
        # Should be sorted newest first
        assert food_items[0].date == "2026-11-03"
        assert food_items[1].date == "2026-11-01"

        # Search category with no entries
        assert manager.filter_by_category("Health") == []

    def test_category_summary(self, manager: ExpenseManager) -> None:
        """Verify accurate calculation of totals, counts, and percentages."""
        manager.add_expense(amount=50.00, category="Food", description="Groceries", date="2026-11-01")
        manager.add_expense(amount=50.00, category="Food", description="Dinner", date="2026-11-02")
        manager.add_expense(amount=100.00, category="Travel", description="Flight ticket", date="2026-11-03")

        # Total is 200.00: Food is 100.00 (50%), Travel is 100.00 (50%)
        summary = manager.get_category_summary()
        assert "Food" in summary
        assert "Travel" in summary

        assert summary["Food"]["total"] == 100.00
        assert summary["Food"]["count"] == 2
        assert summary["Food"]["percentage"] == 50.0

        assert summary["Travel"]["total"] == 100.00
        assert summary["Travel"]["count"] == 1
        assert summary["Travel"]["percentage"] == 50.0

    def test_category_summary_empty(self, manager: ExpenseManager) -> None:
        """Verify category summary on an empty tracker returns an empty dictionary."""
        assert manager.get_category_summary() == {}

