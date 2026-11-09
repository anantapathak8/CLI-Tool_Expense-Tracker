"""Expense model representing an individual expenditure record.

Provides rigorous input validation, immutable identifier generation,
and dictionary serialization/deserialization for persistence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid


@dataclass
class Expense:
    """Represents a single financial expense record.

    Attributes:
        amount (float): The monetary value of the expense (must be strictly positive).
        category (str): The classification of expense (e.g., Food, Travel, Utilities).
        description (str): A brief description of what was purchased.
        date (str): Transaction date in ISO-8601 'YYYY-MM-DD' format.
        id (str): A unique alphanumeric identifier.
    """

    amount: float
    category: str
    description: str
    date: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def __post_init__(self) -> None:
        """Validate all fields after dataclass initialization."""
        self._validate_id()
        self._validate_amount()
        self._validate_category()
        self._validate_description()
        self._validate_date()

    def _validate_id(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Expense ID must be a non-empty string.")
        self.id = self.id.strip()

    def _validate_amount(self) -> None:
        if not isinstance(self.amount, (int, float)):
            raise TypeError(f"Amount must be a numeric value, got {type(self.amount).__name__}.")
        if self.amount <= 0:
            raise ValueError(f"Expense amount must be strictly greater than 0, got {self.amount}.")
        # Store rounded to 2 decimal places for financial consistency
        self.amount = round(float(self.amount), 2)

    def _validate_category(self) -> None:
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValueError("Category must be a non-empty string.")
        self.category = self.category.strip().title()

    def _validate_description(self) -> None:
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("Description must be a non-empty string.")
        self.description = self.description.strip()

    def _validate_date(self) -> None:
        if not isinstance(self.date, str) or not self.date.strip():
            raise ValueError("Date must be a non-empty string in 'YYYY-MM-DD' format.")
        cleaned_date = self.date.strip()
        try:
            parsed = datetime.strptime(cleaned_date, "%Y-%m-%d")
            # Format explicitly to guarantee canonical 'YYYY-MM-DD' representation
            self.date = parsed.strftime("%Y-%m-%d")
        except ValueError as err:
            raise ValueError(
                f"Invalid date format '{cleaned_date}'. Expected 'YYYY-MM-DD' (e.g. 2026-11-09)."
            ) from err

    def to_dict(self) -> dict[str, Any]:
        """Convert the Expense instance into a JSON-serializable dictionary.

        Returns:
            dict[str, Any]: Key-value representation of the expense.
        """
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Expense:
        """Create an Expense instance from a dictionary record.

        Args:
            data (dict[str, Any]): Dictionary containing expense fields.

        Returns:
            Expense: A validated Expense instance.

        Raises:
            KeyError: If required keys are missing in the dictionary.
            ValueError: If values fail validation checks.
            TypeError: If input data is not a dictionary.
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict to construct Expense, got {type(data).__name__}.")

        required_keys = {"id", "amount", "category", "description", "date"}
        missing_keys = required_keys - set(data.keys())
        if missing_keys:
            raise KeyError(f"Missing required fields for Expense: {', '.join(sorted(missing_keys))}")

        return cls(
            id=str(data["id"]),
            amount=float(data["amount"]),
            category=str(data["category"]),
            description=str(data["description"]),
            date=str(data["date"]),
        )

