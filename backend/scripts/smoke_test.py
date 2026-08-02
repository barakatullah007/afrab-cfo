from datetime import UTC, datetime, timedelta
import os
import random
import string
import sys

import requests
from colorama import Fore, init


init(autoreset=True)

BASE_URL = os.getenv(
    "BASE_URL",
    "http://127.0.0.1:8000/api/v1",
)

SUFFIX = "".join(random.choices(string.ascii_lowercase, k=8))
EMAIL = f"test_{SUFFIX}@example.com"
PASSWORD = "Password@123"

TOKEN = None

PASSED = 0
FAILED = 0


def print_title(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def success(name):
    global PASSED
    PASSED += 1
    print(Fore.GREEN + f"[PASS] {name}")


def failure(name, response, expected):
    global FAILED
    FAILED += 1

    print(Fore.RED + f"[FAIL] {name}")
    print(f"Expected : {expected}")
    print(f"Actual   : {response.status_code}")

    print("\nResponse Headers:")
    print(response.headers)

    print("\nResponse Body:")
    try:
        print(response.json())
    except Exception:
        print(response.text)

    print("-" * 70)


def verify(name, response, expected):
    if response.status_code == expected:
        success(name)
        return True

    failure(name, response, expected)
    return False


def auth_headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
    }


def iso_now():
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def iso_future(days: int):
    return (
        datetime.now(UTC)
        .replace(microsecond=0)
        + timedelta(days=days)
    ).isoformat()


print_title("AFRAB CFO Smoke Test")

print_title("Authentication")

register = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "name": "Smoke Test",
        "email": EMAIL,
        "password": PASSWORD,
    },
)

verify(
    "Register",
    register,
    201,
)

login = requests.post(
    f"{BASE_URL}/auth/login",
    data={
        "username": EMAIL,
        "password": PASSWORD,
    },
)

if verify(
    "Login",
    login,
    200,
):
    TOKEN = login.json()["access_token"]
else:
    print(Fore.RED + "Cannot continue without JWT.")
    sys.exit(1)

print_title("Accounts")

create_account = requests.post(
    f"{BASE_URL}/accounts",
    headers=auth_headers(),
    json={
        "name": f"Primary Account {SUFFIX}",
        "type": "bank",
        "opening_balance": 50000,
        "currency": "INR",
        "icon": "fa-solid fa-building-columns",
        "color": "#2563EB",
    },
)

ACCOUNT_ID = None

if verify(
    "Create Account",
    create_account,
    201,
):
    ACCOUNT_ID = create_account.json()["id"]

accounts = requests.get(
    f"{BASE_URL}/accounts",
    headers=auth_headers(),
)

verify(
    "Get Accounts",
    accounts,
    200,
)

if ACCOUNT_ID:
    update_account = requests.put(
        f"{BASE_URL}/accounts/{ACCOUNT_ID}",
        headers=auth_headers(),
        json={
            "name": f"Primary Account Updated {SUFFIX}",
            "type": "bank",
            "opening_balance": 65000,
            "currency": "INR",
            "icon": "fa-solid fa-wallet",
            "color": "#0EA5E9",
        },
    )

    verify(
        "Update Account",
        update_account,
        200,
    )

print_title("Categories")

expense = requests.post(
    f"{BASE_URL}/categories",
    headers=auth_headers(),
    json={
        "name": f"Food {SUFFIX}",
        "type": "expense",
        "icon": "fa-solid fa-utensils",
        "color": "#EF4444",
    },
)

EXPENSE_CATEGORY_ID = None

if verify(
    "Create Expense Category",
    expense,
    201,
):
    EXPENSE_CATEGORY_ID = expense.json()["id"]

income = requests.post(
    f"{BASE_URL}/categories",
    headers=auth_headers(),
    json={
        "name": f"Salary {SUFFIX}",
        "type": "income",
        "icon": "fa-solid fa-wallet",
        "color": "#22C55E",
    },
)

INCOME_CATEGORY_ID = None

if verify(
    "Create Income Category",
    income,
    201,
):
    INCOME_CATEGORY_ID = income.json()["id"]

categories = requests.get(
    f"{BASE_URL}/categories",
    headers=auth_headers(),
)

verify(
    "Get Categories",
    categories,
    200,
)

if EXPENSE_CATEGORY_ID:
    update_category = requests.put(
        f"{BASE_URL}/categories/{EXPENSE_CATEGORY_ID}",
        headers=auth_headers(),
        json={
            "name": f"Dining {SUFFIX}",
            "icon": "fa-solid fa-utensils",
            "color": "#F97316",
        },
    )

    verify(
        "Update Category",
        update_category,
        200,
    )

print_title("Transactions")

TRANSACTION_ID = None

if ACCOUNT_ID and EXPENSE_CATEGORY_ID:
    transaction = requests.post(
        f"{BASE_URL}/transactions",
        headers=auth_headers(),
        json={
            "account_id": ACCOUNT_ID,
            "category_id": EXPENSE_CATEGORY_ID,
            "amount": 250,
            "description": "Lunch",
            "merchant": "KFC",
            "notes": "Smoke test transaction",
            "transaction_date": iso_now(),
        },
    )

    if verify(
        "Create Transaction",
        transaction,
        201,
    ):
        TRANSACTION_ID = transaction.json()["id"]

transactions = requests.get(
    f"{BASE_URL}/transactions",
    headers=auth_headers(),
)

verify(
    "Get Transactions",
    transactions,
    200,
)

if TRANSACTION_ID and ACCOUNT_ID and EXPENSE_CATEGORY_ID:
    get_transaction = requests.get(
        f"{BASE_URL}/transactions/{TRANSACTION_ID}",
        headers=auth_headers(),
    )

    verify(
        "Get Transaction",
        get_transaction,
        200,
    )

    update_transaction = requests.put(
        f"{BASE_URL}/transactions/{TRANSACTION_ID}",
        headers=auth_headers(),
        json={
            "account_id": ACCOUNT_ID,
            "category_id": EXPENSE_CATEGORY_ID,
            "amount": 300,
            "description": "Dinner",
            "merchant": "Domino's",
            "notes": "Updated smoke test transaction",
            "transaction_date": iso_now(),
        },
    )

    verify(
        "Update Transaction",
        update_transaction,
        200,
    )

print_title("Dashboard")

summary = requests.get(
    f"{BASE_URL}/dashboard/summary",
    headers=auth_headers(),
)

verify(
    "Dashboard Summary",
    summary,
    200,
)

recent = requests.get(
    f"{BASE_URL}/dashboard/recent-transactions",
    headers=auth_headers(),
)

verify(
    "Dashboard Recent Transactions",
    recent,
    200,
)

print_title("Budgets")

BUDGET_ID = None

if EXPENSE_CATEGORY_ID:
    budget = requests.post(
        f"{BASE_URL}/budgets",
        headers=auth_headers(),
        json={
            "category_id": EXPENSE_CATEGORY_ID,
            "month": datetime.now(UTC).month,
            "year": datetime.now(UTC).year,
            "amount": 5000,
        },
    )

    if verify(
        "Create Budget",
        budget,
        201,
    ):
        BUDGET_ID = budget.json()["id"]

budgets = requests.get(
    f"{BASE_URL}/budgets",
    headers=auth_headers(),
)

verify(
    "Get Budgets",
    budgets,
    200,
)

if BUDGET_ID:
    get_budget = requests.get(
        f"{BASE_URL}/budgets/{BUDGET_ID}",
        headers=auth_headers(),
    )

    verify(
        "Get Budget",
        get_budget,
        200,
    )

    update_budget = requests.put(
        f"{BASE_URL}/budgets/{BUDGET_ID}",
        headers=auth_headers(),
        json={
            "category_id": EXPENSE_CATEGORY_ID,
            "month": datetime.now(UTC).month,
            "year": datetime.now(UTC).year,
            "amount": 7000,
        },
    )

    verify(
        "Update Budget",
        update_budget,
        200,
    )

if EXPENSE_CATEGORY_ID:
    duplicate = requests.post(
        f"{BASE_URL}/budgets",
        headers=auth_headers(),
        json={
            "category_id": EXPENSE_CATEGORY_ID,
            "month": datetime.now(UTC).month,
            "year": datetime.now(UTC).year,
            "amount": 9999,
        },
    )

    verify(
        "Duplicate Budget",
        duplicate,
        409,
    )

if INCOME_CATEGORY_ID:
    income_budget = requests.post(
        f"{BASE_URL}/budgets",
        headers=auth_headers(),
        json={
            "category_id": INCOME_CATEGORY_ID,
            "month": datetime.now(UTC).month,
            "year": datetime.now(UTC).year,
            "amount": 25000,
        },
    )

    verify(
        "Income Budget",
        income_budget,
        400,
    )

print_title("Goals")

GOAL_ID = None

goal = requests.post(
    f"{BASE_URL}/goals",
    headers=auth_headers(),
    json={
        "name": f"Emergency Fund {SUFFIX}",
        "description": "Six months of expenses",
        "target_amount": 100000,
        "current_amount": 25000,
        "target_date": iso_future(365),
        "priority": "medium",
        "status": "active",
    },
)

if verify(
    "Create Goal",
    goal,
    201,
):
    GOAL_ID = goal.json()["id"]

goals = requests.get(
    f"{BASE_URL}/goals",
    headers=auth_headers(),
)

verify(
    "Get Goals",
    goals,
    200,
)

if GOAL_ID:
    get_goal = requests.get(
        f"{BASE_URL}/goals/{GOAL_ID}",
        headers=auth_headers(),
    )

    verify(
        "Get Goal",
        get_goal,
        200,
    )

    update_goal = requests.put(
        f"{BASE_URL}/goals/{GOAL_ID}",
        headers=auth_headers(),
        json={
            "name": f"Emergency Fund Updated {SUFFIX}",
            "description": "Updated goal",
            "target_amount": 100000,
            "current_amount": 30000,
            "target_date": iso_future(365),
            "priority": "high",
            "status": "active",
        },
    )

    verify(
        "Update Goal",
        update_goal,
        200,
    )

print_title("Recurring Transactions")

RECURRING_TRANSACTION_ID = None

if ACCOUNT_ID and INCOME_CATEGORY_ID:
    recurring = requests.post(
        f"{BASE_URL}/recurring-transactions",
        headers=auth_headers(),
        json={
            "account_id": ACCOUNT_ID,
            "category_id": INCOME_CATEGORY_ID,
            "title": "Monthly Salary",
            "description": "Smoke test recurring salary",
            "amount": 75000,
            "transaction_type": "income",
            "frequency": "monthly",
            "start_date": iso_now(),
            "end_date": iso_future(365),
            "next_run_date": iso_future(30),
        },
    )

    if verify(
        "Create Recurring Transaction",
        recurring,
        201,
    ):
        RECURRING_TRANSACTION_ID = recurring.json()["id"]

recurring_transactions = requests.get(
    f"{BASE_URL}/recurring-transactions",
    headers=auth_headers(),
)

verify(
    "Get Recurring Transactions",
    recurring_transactions,
    200,
)

if RECURRING_TRANSACTION_ID and ACCOUNT_ID and INCOME_CATEGORY_ID:
    get_recurring = requests.get(
        f"{BASE_URL}/recurring-transactions/{RECURRING_TRANSACTION_ID}",
        headers=auth_headers(),
    )

    verify(
        "Get Recurring Transaction",
        get_recurring,
        200,
    )

    update_recurring = requests.put(
        f"{BASE_URL}/recurring-transactions/{RECURRING_TRANSACTION_ID}",
        headers=auth_headers(),
        json={
            "account_id": ACCOUNT_ID,
            "category_id": INCOME_CATEGORY_ID,
            "title": "Monthly Salary Updated",
            "description": "Updated recurring salary",
            "amount": 80000,
            "transaction_type": "income",
            "frequency": "monthly",
            "start_date": iso_now(),
            "end_date": iso_future(365),
            "next_run_date": iso_future(30),
            "is_active": True,
        },
    )

    verify(
        "Update Recurring Transaction",
        update_recurring,
        200,
    )

    deactivate = requests.patch(
        f"{BASE_URL}/recurring-transactions/{RECURRING_TRANSACTION_ID}/deactivate",
        headers=auth_headers(),
    )

    verify(
        "Deactivate Recurring Transaction",
        deactivate,
        200,
    )

    activate = requests.patch(
        f"{BASE_URL}/recurring-transactions/{RECURRING_TRANSACTION_ID}/activate",
        headers=auth_headers(),
    )

    verify(
        "Activate Recurring Transaction",
        activate,
        200,
    )

print_title("Financial Intelligence")

financial_summary = requests.get(
    f"{BASE_URL}/financial-intelligence/summary",
    headers=auth_headers(),
)

verify(
    "Financial Intelligence Summary",
    financial_summary,
    200,
)

budget_utilization = requests.get(
    f"{BASE_URL}/financial-intelligence/budget-utilization",
    headers=auth_headers(),
)

verify(
    "Budget Utilization Insights",
    budget_utilization,
    200,
)

goal_progress = requests.get(
    f"{BASE_URL}/financial-intelligence/goal-progress",
    headers=auth_headers(),
)

verify(
    "Goal Progress Insights",
    goal_progress,
    200,
)

category_insights = requests.get(
    f"{BASE_URL}/financial-intelligence/category-insights",
    headers=auth_headers(),
)

verify(
    "Category Insights",
    category_insights,
    200,
)

monthly_cashflow = requests.get(
    f"{BASE_URL}/financial-intelligence/monthly-cashflow",
    headers=auth_headers(),
)

verify(
    "Monthly Cashflow",
    monthly_cashflow,
    200,
)

print_title("Cleanup")

if RECURRING_TRANSACTION_ID:
    delete_recurring = requests.delete(
        f"{BASE_URL}/recurring-transactions/{RECURRING_TRANSACTION_ID}",
        headers=auth_headers(),
    )

    verify(
        "Delete Recurring Transaction",
        delete_recurring,
        204,
    )

if GOAL_ID:
    delete_goal = requests.delete(
        f"{BASE_URL}/goals/{GOAL_ID}",
        headers=auth_headers(),
    )

    verify(
        "Delete Goal",
        delete_goal,
        204,
    )

if BUDGET_ID:
    delete_budget = requests.delete(
        f"{BASE_URL}/budgets/{BUDGET_ID}",
        headers=auth_headers(),
    )

    verify(
        "Delete Budget",
        delete_budget,
        204,
    )

if TRANSACTION_ID:
    delete_transaction = requests.delete(
        f"{BASE_URL}/transactions/{TRANSACTION_ID}",
        headers=auth_headers(),
    )

    verify(
        "Delete Transaction",
        delete_transaction,
        204,
    )

if EXPENSE_CATEGORY_ID:
    delete_category = requests.delete(
        f"{BASE_URL}/categories/{EXPENSE_CATEGORY_ID}",
        headers=auth_headers(),
    )

    verify(
        "Delete Expense Category",
        delete_category,
        204,
    )

if INCOME_CATEGORY_ID:
    delete_category = requests.delete(
        f"{BASE_URL}/categories/{INCOME_CATEGORY_ID}",
        headers=auth_headers(),
    )

    verify(
        "Delete Income Category",
        delete_category,
        204,
    )

if ACCOUNT_ID:
    delete_account = requests.delete(
        f"{BASE_URL}/accounts/{ACCOUNT_ID}",
        headers=auth_headers(),
    )

    verify(
        "Delete Account",
        delete_account,
        204,
    )

print_title("Result")

print(Fore.GREEN + f"Passed : {PASSED}")
print(Fore.RED + f"Failed : {FAILED}")

if FAILED:
    sys.exit(1)
