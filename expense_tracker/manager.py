"""Business logic layer for managing expenses.

Coordinates operations between in-memory expense entities and the persistence
storage layer, providing methods to add, list, delete, filter, and summarize expenditures.
"""

from __future__ import annotations

from typing import Sequence

from expense_tracker.expense import Expense
from expense_tracker.storage import ExpenseStorage


class ExpenseManager:
    """Orchestrates in-memory expense operations and synchronizes with storage.

    Attributes:
        storage (ExpenseStorage): Storage instance handling file operations.
    """

    def __init__(self, storage: ExpenseStorage) -> None:
        """Initialize the manager and load existing expenses from storage.

        Args:
            storage (ExpenseStorage): Persistence backend.
        """
        self.storage = storage
        self._expenses: list[Expense] = self.storage.load()

    @property
    def expenses(self) -> list[Expense]:
        """Return a defensive copy of all loaded expenses."""
        return list(self._expenses)

    def add_expense(
        self,
        amount: float,
        category: str,
        description: str,
        date: str,
        expense_id: str | None = None,
    ) -> Expense:
        """Create, validate, add, and persist a new expense.

        Args:
            amount (float): Positive monetary value.
            category (str): Expenditure category.
            description (str): Description of the purchase.
            date (str): Transaction date ('YYYY-MM-DD').
            expense_id (str | None): Optional unique ID; generated automatically if omitted.

        Returns:
            Expense: The created and stored Expense object.
        """
        kwargs = {
            "amount": amount,
            "category": category,
            "description": description,
            "date": date,
        }
        if expense_id is not None:
            kwargs["id"] = expense_id

        expense = Expense(**kwargs)
        self._expenses.append(expense)
        self.storage.save(self._expenses)
        return expense

    def list_expenses(self, sort_by_date_desc: bool = True) -> list[Expense]:
        """Retrieve all expenses, optionally ordered by date descending.

        Args:
            sort_by_date_desc (bool): Whether to sort records from newest to oldest.

        Returns:
            list[Expense]: A list of expense records.
        """
        if sort_by_date_desc:
            return sorted(self._expenses, key=lambda x: x.date, reverse=True)
        return list(self._expenses)

    def get_expense_by_id(self, expense_id: str) -> Expense | None:
        """Look up an expense by its unique identifier.

        Args:
            expense_id (str): The ID to search for.

        Returns:
            Expense | None: The matching Expense, or None if not found.
        """
        target_id = expense_id.strip()
        for expense in self._expenses:
            if expense.id == target_id:
                return expense
        return None

    def delete_expense(self, expense_id: str) -> Expense:
        """Delete an expense record by its unique ID and persist the updated list.

        Args:
            expense_id (str): The unique ID of the record to remove.

        Returns:
            Expense: The removed Expense object.

        Raises:
            KeyError: If no record with the provided ID exists.
        """
        target = self.get_expense_by_id(expense_id)
        if target is None:
            raise KeyError(f"Expense with ID '{expense_id}' was not found.")

        self._expenses.remove(target)
        self.storage.save(self._expenses)
        return target

    def calculate_total(self, expenses: Sequence[Expense] | None = None) -> float:
        """Calculate the sum of amounts for the provided expenses or all expenses.

        Args:
            expenses (Sequence[Expense] | None): Subset of expenses to sum.
                Defaults to all stored expenses.

        Returns:
            float: Total amount rounded to 2 decimal places.
        """
        records = self._expenses if expenses is None else expenses
        total = sum(exp.amount for exp in records)
        return round(float(total), 2)

    def filter_by_category(self, category: str) -> list[Expense]:
        """Filter expenses by category (case-insensitive).

        Args:
            category (str): The category name to search for.

        Returns:
            list[Expense]: All matching expense records, newest first.
        """
        query = category.strip().lower()
        matches = [exp for exp in self._expenses if exp.category.lower() == query]
        return sorted(matches, key=lambda x: x.date, reverse=True)

    def get_category_summary(self) -> dict[str, dict[str, float]]:
        """Compute category-wise breakdown including totals, transaction count, and percentages.

        Returns:
            dict[str, dict[str, float]]: Mapping of category name to a dict with:
                - 'total': Total amount spent in this category.
                - 'count': Number of expenses in this category.
                - 'percentage': Percentage of total spending (0.0 to 100.0).
        """
        grand_total = self.calculate_total()
        summary: dict[str, dict[str, float]] = {}

        for exp in self._expenses:
            if exp.category not in summary:
                summary[exp.category] = {"total": 0.0, "count": 0, "percentage": 0.0}
            summary[exp.category]["total"] += exp.amount
            summary[exp.category]["count"] += 1

        for cat_data in summary.values():
            cat_data["total"] = round(cat_data["total"], 2)
            if grand_total > 0:
                cat_data["percentage"] = round((cat_data["total"] / grand_total) * 100, 2)
            else:
                cat_data["percentage"] = 0.0

        return summary

