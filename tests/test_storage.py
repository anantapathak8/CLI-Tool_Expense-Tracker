"""Unit tests for the ExpenseStorage persistence layer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from expense_tracker.expense import Expense
from expense_tracker.storage import CorruptedDataError, ExpenseStorage, StorageError


class TestExpenseStorage:
    """Test suite for ExpenseStorage file persistence."""

    def test_missing_file_returns_empty_list(self, tmp_path: Path) -> None:
        """Verify that a non-existent file returns an empty list without raising errors."""
        non_existent = tmp_path / "subdir" / "missing.json"
        storage = ExpenseStorage(non_existent)
        assert storage.load() == []

    def test_save_and_load_cycle(self, tmp_path: Path) -> None:
        """Verify that expenses can be saved and accurately loaded back."""
        file_path = tmp_path / "data" / "expenses.json"
        storage = ExpenseStorage(file_path)

        expenses = [
            Expense(id="id-1", amount=15.75, category="Food", description="Lunch", date="2026-11-08"),
            Expense(id="id-2", amount=40.00, category="Travel", description="Fuel", date="2026-11-09"),
        ]

        storage.save(expenses)
        assert file_path.exists()

        loaded = storage.load()
        assert len(loaded) == 2
        assert loaded[0].id == "id-1"
        assert loaded[0].amount == 15.75
        assert loaded[0].category == "Food"
        assert loaded[1].id == "id-2"
        assert loaded[1].amount == 40.00
        assert loaded[1].category == "Travel"

    def test_corrupted_json_syntax_raises_corrupted_data_error(self, tmp_path: Path) -> None:
        """Verify that malformed JSON raises CorruptedDataError without overwriting data."""
        file_path = tmp_path / "corrupted.json"
        file_path.write_text("{ this is broken JSON !! ]", encoding="utf-8")

        storage = ExpenseStorage(file_path)
        with pytest.raises(CorruptedDataError, match="corrupted or invalid JSON"):
            storage.load()

        # Ensure the corrupted file content was not destroyed or cleared
        assert file_path.read_text(encoding="utf-8") == "{ this is broken JSON !! ]"

    def test_non_list_root_raises_corrupted_data_error(self, tmp_path: Path) -> None:
        """Verify that a JSON root that is a dict instead of a list raises CorruptedDataError."""
        file_path = tmp_path / "bad_root.json"
        file_path.write_text(json.dumps({"expenses": []}), encoding="utf-8")

        storage = ExpenseStorage(file_path)
        with pytest.raises(CorruptedDataError, match="Expected root JSON list"):
            storage.load()

    def test_invalid_record_content_raises_corrupted_data_error(self, tmp_path: Path) -> None:
        """Verify that valid JSON containing invalid Expense records raises CorruptedDataError."""
        file_path = tmp_path / "bad_record.json"
        malformed_records = [
            {
                "id": "exp-1",
                "amount": -50.00,  # Invalid negative amount
                "category": "Food",
                "description": "Lunch",
                "date": "2026-11-09",
            }
        ]
        file_path.write_text(json.dumps(malformed_records), encoding="utf-8")

        storage = ExpenseStorage(file_path)
        with pytest.raises(CorruptedDataError, match="Corrupted record at index 0"):
            storage.load()

    def test_unicode_and_special_characters_persisted(self, tmp_path: Path) -> None:
        """Verify that non-ASCII unicode text in descriptions is preserved."""
        file_path = tmp_path / "unicode.json"
        storage = ExpenseStorage(file_path)

        expense = Expense(
            id="uni-1",
            amount=8.50,
            category="Café",
            description="Café au lait & croissant 🥐",
            date="2026-11-09",
        )
        storage.save([expense])

        loaded = storage.load()
        assert len(loaded) == 1
        assert loaded[0].category == "Café"
        assert loaded[0].description == "Café au lait & croissant 🥐"

