from enum import Enum


class SavingsAllocationType(str, Enum):
    EMERGENCY_FUND = "emergency_fund"
    INVESTMENT = "investment"
    OTHER = "other"
