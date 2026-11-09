# Personal Expense Tracker — Command Line Application

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Testing](https://img.shields.io/badge/Tests-44%20Passed%20%7C%20Pytest-brightgreen.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-Layered%20%2F%20Modular-informational.svg)]()

A robust, beginner-friendly, and professionally structured Python command-line application for tracking, analyzing, and persisting personal financial expenditures.

Developed as a Week 4 Capstone Project in the Python and Software Engineering Acceleration Program for an undergraduate curriculum in Robotics and Artificial Intelligence.

---

## 🌟 Key Features

1. **Rich Expense Model (`Expense`)**:
   - Unique 8-character alphanumeric identifier for easy terminal interaction.
   - Strictly positive numeric amount validation (rounded to 2 decimal places for monetary precision).
   - Category normalization (auto-trimmed and title-cased).
   - Non-empty description validation.
   - ISO-8601 standard date validation (`YYYY-MM-DD`).
   - Clean serialization (`to_dict`) and deserialization (`from_dict`).

2. **Decoupled Business Logic (`ExpenseManager`)**:
   - Add new expenses and immediately synchronize state.
   - View all expenses sorted chronologically in descending order.
   - Retrieve or delete records safely by unique ID with user confirmation prompts.
   - Calculate aggregate expenditure accurately.
   - Case-insensitive category filtering.
   - Multi-metric category summaries with expense counts, sub-totals, and expenditure percentages.

3. **Resilient Persistence Engine (`ExpenseStorage`)**:
   - **Atomic File Writes**: Writes records to an intermediate `.tmp` file and replaces the destination using OS atomic file system operations (`os.replace`), preventing partial writes or file corruption during unexpected power cuts or aborts.
   - **Missing-File Tolerance**: Gracefully initializes a fresh state if the target JSON database does not yet exist.
   - **Corruption Protection**: Raises custom `CorruptedDataError` without overwriting or destroying corrupted files, safeguarding user data for manual recovery.

4. **Interactive Command-Line Interface (`ExpenseCLI`)**:
   - Menu-driven text UI with continuous re-prompting on invalid inputs.
   - Polished ASCII table formatting with aligned monetary amounts and category columns.
   - Defaulting date inputs to today's date on `[Enter]`.
   - Graceful termination on user exit or standard POSIX / Windows interruptions (`Ctrl+C`, `EOF`).

5. **Exhaustive Automated Test Suite**:
   - 44 comprehensive unit and end-to-end integration tests using `pytest`.
   - Utilizes temporary directory fixtures (`tmp_path`) and monkeypatched `stdin`/`stdout` so production data files are never modified during test execution.

---

## 📂 Project Architecture

The project adheres to a clean layered architecture, enforcing the **Single Responsibility Principle (SRP)**:

```text
CLI_Expense_Tracker/
│
├── expense_tracker/            # Core application package
│   ├── __init__.py             # Package declaration & metadata
│   ├── expense.py              # Domain entity (Expense model & validation)
│   ├── manager.py              # Business logic orchestrator (ExpenseManager)
│   ├── storage.py              # Persistence layer (JSON atomic read/write)
│   ├── cli.py                  # User interface (Menu, inputs, table rendering)
│   └── main.py                 # Application bootstrapper and dependency wire-up
│
├── tests/                      # Automated test suite
│   ├── __init__.py
│   ├── test_expense.py         # Tests for Expense validation & serialization
│   ├── test_manager.py         # Tests for CRUD & analytics calculations
│   ├── test_storage.py         # Tests for persistence, atomic saves & corruption handling
│   ├── test_cli.py             # Tests for terminal prompts & handlers
│   └── test_integration.py     # End-to-end integration test through main()
│
├── data/                       # Default storage directory (git-ignored)
│   └── .gitkeep
│
├── main.py                     # Convenience root launcher
├── requirements.txt            # Project test dependencies
├── .gitignore                  # Git ignore rules for Python and runtime data
├── LICENSE                     # MIT License
└── README.md                   # Comprehensive technical documentation
```

### Layer Interaction Flow

```
[ User Terminal ]
       ↕ (stdin / stdout)
[ ExpenseCLI ]  (Input parsing, formatters, validation)
       ↕
[ ExpenseManager ]  (Business rules, filtering, aggregation)
       ↕                                  ↕
[ Expense Model ] (Data invariants)   [ ExpenseStorage ] (JSON & Atomic I/O)
                                                 ↕
                                      [ data/expenses.json ]
```

---

## 🛠️ Prerequisites & Setup

### Requirements
- **Operating System**: Windows, macOS, or Linux
- **Python**: Version `3.10.6` or higher
- **Package Manager**: `pip`

### Step 1: Clone or Navigate to the Workspace
Open PowerShell or Command Prompt in the project directory:
```powershell
cd c:\Users\anant\OneDrive\Desktop\CLI_Expense_Tracker
```

### Step 2: Create and Activate a Virtual Environment
```powershell
# Create a virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# (Alternative) Activate on Windows (CMD)
.\venv\Scripts\activate.bat
```

### Step 3: Install Test Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🚀 Running the Application

Launch the application using either the root convenience script:
```powershell
python main.py
```
Or run as a package module:
```powershell
python -m expense_tracker.main
```

### Custom Storage Location (Optional)
To use a custom database path, set the `EXPENSE_TRACKER_FILE` environment variable:
```powershell
$env:EXPENSE_TRACKER_FILE="C:\path\to\my_expenses.json"
python main.py
```

---

## 💻 CLI Usage Guide

### Main Menu
```text
==============================================================
         PERSONAL EXPENSE TRACKER - CLI APPLICATION           
==============================================================
 Track daily spending, inspect categories, and take control!  
--------------------------------------------------------------

----------------------- MAIN MENU ----------------------------
  [1] Add Expense
  [2] View All Expenses
  [3] Delete Expense
  [4] Calculate Total Expenditure
  [5] Filter by Category
  [6] Category-wise Summary
  [7] Exit
--------------------------------------------------------------
Enter choice (1-7):
```

### Example 1: Adding an Expense
```text
Enter choice (1-7): 1

--- ADD NEW EXPENSE ---
Enter amount (e.g. 24.50): 18.50
 (Suggested: Food, Travel, Utilities, Books, Health, Entertainment)
Enter category: Food
Enter description: College Cafeteria Lunch
Enter date (YYYY-MM-DD) [Press Enter for Today: 2026-11-09]: [Enter]

[+] Expense successfully added! (ID: a3f89b1c)
```

### Example 2: Viewing All Expenses
```text
Enter choice (1-7): 2

--- ALL RECORDED EXPENSES (Total: 3 items) ---
-------------------------------------------------------------------------------------
ID         | Date       | Category        |     Amount | Description
-------------------------------------------------------------------------------------
a3f89b1c   | 2026-11-09 | Food            |     $18.50 | College Cafeteria Lunch
c214d0ea   | 2026-11-08 | Books           |     $45.00 | Robotics & AI Textbook
e581290f   | 2026-11-07 | Travel          |     $12.00 | Metro Pass Recharge
-------------------------------------------------------------------------------------
Grand Total: $75.50
```

### Example 3: Category-Wise Breakdown Summary
```text
Enter choice (1-7): 6

--- CATEGORY-WISE SPENDING SUMMARY ---
-----------------------------------------------------
Category           | Count   |  Total Spent | Percentage
-----------------------------------------------------
Books              | 1       |       $45.00 |      59.6%
Food               | 1       |       $18.50 |      24.5%
Travel             | 1       |       $12.00 |      15.9%
-----------------------------------------------------
GRAND TOTAL        | 3       |       $75.50 |    100.0%
```

### Example 4: Deleting an Expense
```text
Enter choice (1-7): 3

--- DELETE EXPENSE ---
Enter the ID of the expense to delete: e581290f
Found record: [2026-11-07] Travel - $12.00 (Metro Pass Recharge)
Are you sure you want to delete this record? (y/N): y
[+] Successfully deleted expense (ID: e581290f).
```

---

## 🧪 Running Automated Tests

The application features a 44-test suite validating business rules, edge cases, input errors, and file corruption behaviors.

### Run All Tests
```powershell
python -m pytest -v
```

### Run with Coverage (if `pytest-cov` is installed)
```powershell
python -m pytest --tb=short
```

### Test Suite Structure
| Test Module | Coverage Scope | Test Count |
| :--- | :--- | :---: |
| `tests/test_expense.py` | Dataclass invariants, negative amounts, invalid dates, ID generation, serialization | 13 |
| `tests/test_manager.py` | Add, sort, delete, total sum, category search, category percentages | 10 |
| `tests/test_storage.py` | Missing files, atomic write verification, JSON decode corruption, non-list root | 6 |
| `tests/test_cli.py` | Terminal loops, prompt re-tries, table outputs, confirmation workflows | 14 |
| `tests/test_integration.py` | End-to-end session simulation through `main()` entrypoint | 1 |
| **Total** | | **44 Passed** |

---

## 🛡️ Software Engineering Highlights

1. **Defensive Programming & Fail-Safe Persistence**:
   - Writes are directed to `.tmp` files before being atomically swapped with target files. This guarantees that power interruptions or unexpected system reboots cannot leave the JSON file corrupted with partial writes.
   - If a file is tampered with or corrupted, the system halts with a detailed diagnostic message rather than wiping out the file with empty contents.

2. **Decoupled Architecture**:
   - The user interface knows only about the `ExpenseManager` contract.
   - The `ExpenseManager` knows only the `ExpenseStorage` interface.
   - Storage does not care how expenses are displayed or manipulated.

3. **Academic Portfolio Standard**:
   - Conforms to **PEP 8** style guidelines.
   - Python 3.10 standard library compliance (`typing`, `dataclasses`, `pathlib`).
   - Clean type annotations across all signatures.
   - 100% test isolation with zero side-effects on user data during test executions.

---

## 🔭 Future Roadmap & Enhancements

While intentionally kept lean and dependency-free for educational clarity, the following enhancements can be built on top of this architecture:
- [ ] Export transactions to CSV or PDF summary reports.
- [ ] Monthly budgeting thresholds with warning indicators when a category exceeds 80%.
- [ ] Multi-currency support with dynamic conversion rates.
- [ ] SQLite persistence backend implementing the same storage interface.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — see the LICENSE file for details.

