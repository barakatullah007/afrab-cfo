from enum import Enum


class MemoryType(str, Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    PREFERENCE = "preference"
    FINANCIAL_CONTEXT = "financial_context"
