import random
import string
import sys

import requests
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "http://127.0.0.1:8000/api/v1"

EMAIL = (
    f"test_{''.join(random.choices(string.ascii_lowercase, k=8))}"
    "@example.com"
)
PASSWORD = "Password@123"

TOKEN = None
ACCOUNT_ID = None
EXPENSE_CATEGORY_ID = None
INCOME_CATEGORY_ID = None
TRANSACTION_ID = None
BUDGET_ID = None

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
        "Authorization": f"Bearer {TOKEN}"
    }


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
    sys.exit()
    
print_title("Accounts")


create_account = requests.post(
    f"{BASE_URL}/accounts",
    headers=auth_headers(),
    json={
        "name": "Primary Account",
        "type": "bank",
        "opening_balance": 50000,
        "currency": "INR",
        "icon": "fa-solid fa-building-columns",
        "color": "#2563EB",
    },
)

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

    update = requests.put(
    f"{BASE_URL}/accounts/{ACCOUNT_ID}",
    headers=auth_headers(),
    json={
        "name": "Primary Account Updated",
        "type": "bank",
        "opening_balance": 65000,
        "currency": "INR",
        "icon": "fa-solid fa-wallet",
        "color": "#0EA5E9",
    },
)
print_title("Current Result")

print(Fore.GREEN + f"Passed : {PASSED}")
print(Fore.RED + f"Failed : {FAILED}")

print_title("Categories")

# ---------------- Create Expense Category ----------------

expense = requests.post(
    f"{BASE_URL}/categories",
    headers=auth_headers(),
    json={
        "name": "Food",
        "type": "expense",
        "icon": "fa-solid fa-utensils",
        "color": "#EF4444",
    },
)

if verify("Create Expense Category", expense, 201):
    EXPENSE_CATEGORY_ID = expense.json()["id"]

# ---------------- Create Income Category ----------------

income = requests.post(
    f"{BASE_URL}/categories",
    headers=auth_headers(),
    json={
        "name": "Salary",
        "type": "income",
        "icon": "fa-solid fa-wallet",
        "color": "#22C55E",
    },
)

if verify("Create Income Category", income, 201):
    INCOME_CATEGORY_ID = income.json()["id"]

# ---------------- Get Categories ----------------

categories = requests.get(
    f"{BASE_URL}/categories",
    headers=auth_headers(),
)

verify("Get Categories", categories, 200)

print_title("Transactions")

transaction = requests.post(
    f"{BASE_URL}/transactions",
    headers=auth_headers(),
    json={
        "account_id": ACCOUNT_ID,
        "category_id": EXPENSE_CATEGORY_ID,
        "type": "expense",
        "amount": 250,
        "description": "Lunch",
        "transaction_date": "2026-08-02"
    },
)

if verify("Create Transaction", transaction, 201):
    TRANSACTION_ID = transaction.json()["id"]


transactions = requests.get(
    f"{BASE_URL}/transactions",
    headers=auth_headers(),
)

verify("Get Transactions", transactions, 200)

print_title("Dashboard")

summary = requests.get(
    f"{BASE_URL}/dashboard/summary",
    headers=auth_headers(),
)

verify("Dashboard Summary", summary, 200)


recent = requests.get(
    f"{BASE_URL}/dashboard/recent-transactions",
    headers=auth_headers(),
)

verify("Dashboard Recent Transactions", recent, 200)

print_title("Dashboard")

summary = requests.get(
    f"{BASE_URL}/dashboard/summary",
    headers=auth_headers(),
)

verify("Dashboard Summary", summary, 200)


recent = requests.get(
    f"{BASE_URL}/dashboard/recent-transactions",
    headers=auth_headers(),
)

verify("Dashboard Recent Transactions", recent, 200)
print_title("Budgets")

# ---------------- Create Budget ----------------

budget = requests.post(
    f"{BASE_URL}/budgets",
    headers=auth_headers(),
    json={
        "category_id": EXPENSE_CATEGORY_ID,
        "month": 8,
        "year": 2026,
        "amount": 5000,
    },
)

if verify("Create Budget", budget, 201):
    BUDGET_ID = budget.json()["id"]

# ---------------- Get Budgets ----------------

budgets = requests.get(
    f"{BASE_URL}/budgets",
    headers=auth_headers(),
)

verify(
    "Get Budgets",
    budgets,
    200,
)

# ---------------- Get Budget ----------------

if BUDGET_ID:

    budget = requests.get(
        f"{BASE_URL}/budgets/{BUDGET_ID}",
        headers=auth_headers(),
    )

    verify(
        "Get Budget",
        budget,
        200,
    )

# ---------------- Update Budget ----------------

if BUDGET_ID:

    budget = requests.put(
        f"{BASE_URL}/budgets/{BUDGET_ID}",
        headers=auth_headers(),
        json={
            "category_id": EXPENSE_CATEGORY_ID,
            "month": 8,
            "year": 2026,
            "amount": 7000,
        },
    )

    verify(
        "Update Budget",
        budget,
        200,
    )

# ---------------- Duplicate ----------------

duplicate = requests.post(
    f"{BASE_URL}/budgets",
    headers=auth_headers(),
    json={
        "category_id": EXPENSE_CATEGORY_ID,
        "month": 8,
        "year": 2026,
        "amount": 9999,
    },
)

verify(
    "Duplicate Budget",
    duplicate,
    409,
)

# ---------------- Income Budget ----------------

income_budget = requests.post(
    f"{BASE_URL}/budgets",
    headers=auth_headers(),
    json={
        "category_id": INCOME_CATEGORY_ID,
        "month": 8,
        "year": 2026,
        "amount": 25000,
    },
)

verify(
    "Income Budget",
    income_budget,
    400,
)

# ---------------- Delete ----------------

if BUDGET_ID:

    delete = requests.delete(
        f"{BASE_URL}/budgets/{BUDGET_ID}",
        headers=auth_headers(),
    )

    verify(
        "Delete Budget",
        delete,
        204,
    )