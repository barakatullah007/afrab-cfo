from enum import Enum


class AccountType(str, Enum):
    CASH = "cash"
    BANK = "bank"
    WALLET = "wallet"
    CREDIT_CARD = "credit_card"
    SAVINGS = "savings"
    INVESTMENT = "investment"