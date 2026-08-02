from enum import Enum


class RecurringFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class RecurringTransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
