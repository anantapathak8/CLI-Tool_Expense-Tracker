"""Command-Line Interface (CLI) for the Personal Expense Tracker.

Provides an interactive text-based user interface with formatted tabular output,
robust input validation, and graceful error handling.
"""

from __future__ import annotations

from datetime import datetime
import sys
from typing import Sequence

from expense_tracker.expense import Expense
from expense_tracker.manager import ExpenseManager
from expense_tracker.storage import CorruptedDataError, StorageError


class ExpenseCLI:
    """Terminal user interface orchestrator."""

    DEFAULT_CURRENCY = "$"

    def __init__(self, manager: ExpenseManager) -> None:
        """Initialize the CLI with an ExpenseManager instance.

        Args:
            manager (ExpenseManager): The active expense manager.
        """
        self.manager = manager

    def display_banner(self) -> None:
        """Render the welcome banner."""
        banner = """
==============================================================
         PERSONAL EXPENSE TRACKER - CLI APPLICATION           
==============================================================
 Track daily spending, inspect categories, and take control!  
--------------------------------------------------------------"""
        print(banner)

    def display_menu(self) -> None:
        """Display the primary user menu options."""
        menu = """
----------------------- MAIN MENU ----------------------------
  [1] Add Expense
  [2] View All Expenses
  [3] Delete Expense
  [4] Calculate Total Expenditure
  [5] Filter by Category
  [6] Category-wise Summary
  [7] Exit
--------------------------------------------------------------"""
        print(menu)

    def run(self) -> None:
        """Run the main interactive menu loop."""
        self.display_banner()
        while True:
            try:
                self.display_menu()
                choice = input("Enter choice (1-7): ").strip()

                if choice == "1":
                    self.handle_add_expense()
                elif choice == "2":
                    self.handle_view_all()
                elif choice == "3":
                    self.handle_delete_expense()
                elif choice == "4":
                    self.handle_calculate_total()
                elif choice == "5":
                    self.handle_filter_by_category()
                elif choice == "6":
                    self.handle_category_summary()
                elif choice == "7":
                    print("\nThank you for using Personal Expense Tracker. Goodbye!\n")
                    break
                else:
                    print("\n[!] Invalid selection. Please enter a number between 1 and 7.")
            except (KeyboardInterrupt, EOFError):
                print("\n\nSession interrupted. Exiting gracefully. Goodbye!\n")
                break
            except StorageError as err:
                print(f"\n[Storage Error] An unexpected file issue occurred: {err}")
            except Exception as err:  # Defensive catch for unexpected runtime issues
                print(f"\n[Unexpected Error] {err}")

    # ------------------------------------------------------------------
    # Input Helper Methods
    # ------------------------------------------------------------------

    def prompt_amount(self) -> float:
        """Prompt user for a valid positive monetary amount."""
        while True:
            raw = input("Enter amount (e.g. 24.50): ").strip()
            if not raw:
                print(" [!] Amount cannot be blank. Please try again.")
                continue
            try:
                val = float(raw)
                if val <= 0:
                    print(" [!] Amount must be strictly greater than 0. Please try again.")
                    continue
                return round(val, 2)
            except ValueError:
                print(" [!] Invalid numeric input. Please enter a valid number (e.g. 15.00).")

    def prompt_category(self) -> str:
        """Prompt user for a non-empty category name."""
        suggestions = "Suggested: Food, Travel, Utilities, Books, Health, Entertainment"
        print(f" ({suggestions})")
        while True:
            raw = input("Enter category: ").strip()
            if not raw:
                print(" [!] Category cannot be blank. Please enter a category name.")
                continue
            return raw.title()

    def prompt_description(self) -> str:
        """Prompt user for a non-empty description."""
        while True:
            raw = input("Enter description: ").strip()
            if not raw:
                print(" [!] Description cannot be blank. Please enter a brief description.")
                continue
            return raw

    def prompt_date(self) -> str:
        """Prompt user for a date in 'YYYY-MM-DD' format, defaulting to today."""
        today = datetime.now().strftime("%Y-%m-%d")
        while True:
            raw = input(f"Enter date (YYYY-MM-DD) [Press Enter for Today: {today}]: ").strip()
            if not raw:
                return today
            try:
                parsed = datetime.strptime(raw, "%Y-%m-%d")
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                print(" [!] Invalid date format. Please use 'YYYY-MM-DD' (e.g. 2026-11-09).")

    # ------------------------------------------------------------------
    # Table Formatting Helpers
    # ------------------------------------------------------------------

    def render_expenses_table(self, expenses: Sequence[Expense], title: str = "EXPENSES") -> None:
        """Render a formatted ASCII table of expense records."""
        if not expenses:
            print(f"\nNo records found for: {title}")
            return

        print(f"\n--- {title} (Total: {len(expenses)} item{'s' if len(expenses) != 1 else ''}) ---")
        header = f"{'ID':<10} | {'Date':<10} | {'Category':<15} | {'Amount':>10} | {'Description'}"
        separator = "-" * len(header) + "-" * 20
        print(separator)
        print(header)
        print(separator)

        for exp in expenses:
            amt_str = f"{self.DEFAULT_CURRENCY}{exp.amount:,.2f}"
            print(f"{exp.id:<10} | {exp.date:<10} | {exp.category:<15} | {amt_str:>10} | {exp.description}")

        print(separator)

    # ------------------------------------------------------------------
    # Action Handlers
    # ------------------------------------------------------------------

    def handle_add_expense(self) -> None:
        """Handle Option 1: Add a new expense."""
        print("\n--- ADD NEW EXPENSE ---")
        amount = self.prompt_amount()
        category = self.prompt_category()
        description = self.prompt_description()
        date = self.prompt_date()

        try:
            created = self.manager.add_expense(
                amount=amount,
                category=category,
                description=description,
                date=date,
            )
            print(f"\n[+] Expense successfully added! (ID: {created.id})")
        except ValueError as err:
            print(f"\n[!] Failed to add expense: {err}")

    def handle_view_all(self) -> None:
        """Handle Option 2: View all recorded expenses."""
        expenses = self.manager.list_expenses()
        self.render_expenses_table(expenses, title="ALL RECORDED EXPENSES")
        total = self.manager.calculate_total(expenses)
        print(f"Grand Total: {self.DEFAULT_CURRENCY}{total:,.2f}\n")

    def handle_delete_expense(self) -> None:
        """Handle Option 3: Delete an expense by ID."""
        print("\n--- DELETE EXPENSE ---")
        target_id = input("Enter the ID of the expense to delete: ").strip()
        if not target_id:
            print("[!] Expense ID cannot be empty.")
            return

        expense = self.manager.get_expense_by_id(target_id)
        if expense is None:
            print(f"[!] No expense found with ID '{target_id}'.")
            return

        # Show record details before confirmation
        print(
            f"Found record: [{expense.date}] {expense.category} - "
            f"{self.DEFAULT_CURRENCY}{expense.amount:,.2f} ({expense.description})"
        )
        confirm = input("Are you sure you want to delete this record? (y/N): ").strip().lower()
        if confirm in ("y", "yes"):
            try:
                deleted = self.manager.delete_expense(target_id)
                print(f"[+] Successfully deleted expense (ID: {deleted.id}).")
            except KeyError as err:
                print(f"[!] Delete failed: {err}")
        else:
            print("[-] Deletion cancelled.")

    def handle_calculate_total(self) -> None:
        """Handle Option 4: Calculate total expenditure."""
        print("\n--- TOTAL EXPENDITURE ---")
        total = self.manager.calculate_total()
        count = len(self.manager.expenses)
        print(f"Total Transactions : {count}")
        print(f"Total Expenditure  : {self.DEFAULT_CURRENCY}{total:,.2f}\n")

    def handle_filter_by_category(self) -> None:
        """Handle Option 5: Filter expenses by category."""
        print("\n--- FILTER BY CATEGORY ---")
        category = input("Enter category to search: ").strip()
        if not category:
            print("[!] Category query cannot be empty.")
            return

        matches = self.manager.filter_by_category(category)
        if not matches:
            print(f"\n[i] No expenses found under category '{category.title()}'.")
            return

        self.render_expenses_table(matches, title=f"EXPENSES IN CATEGORY: {category.title()}")
        subtotal = self.manager.calculate_total(matches)
        print(f"Subtotal for {category.title()}: {self.DEFAULT_CURRENCY}{subtotal:,.2f}\n")

    def handle_category_summary(self) -> None:
        """Handle Option 6: Generate category-wise spending breakdown."""
        print("\n--- CATEGORY-WISE SPENDING SUMMARY ---")
        summary = self.manager.get_category_summary()
        if not summary:
            print("[i] No expense records available to summarize.")
            return

        grand_total = self.manager.calculate_total()
        header = f"{'Category':<18} | {'Count':<7} | {'Total Spent':>12} | {'Percentage':>10}"
        separator = "-" * len(header)
        print(separator)
        print(header)
        print(separator)

        # Sort summary by total spent descending
        sorted_summary = sorted(summary.items(), key=lambda item: item[1]["total"], reverse=True)
        for cat, data in sorted_summary:
            spent_str = f"{self.DEFAULT_CURRENCY}{data['total']:,.2f}"
            pct_str = f"{data['percentage']:.1f}%"
            print(f"{cat:<18} | {int(data['count']):<7} | {spent_str:>12} | {pct_str:>10}")

        print(separator)
        print(f"{'GRAND TOTAL':<18} | {len(self.manager.expenses):<7} | {self.DEFAULT_CURRENCY}{grand_total:>11,.2f} |    100.0%\n")

