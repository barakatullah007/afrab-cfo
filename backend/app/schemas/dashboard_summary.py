from decimal import Decimal

from pydantic import BaseModel


class DashboardSummary(BaseModel):

    total_balance: Decimal

    monthly_income: Decimal

    monthly_expense: Decimal

    savings: Decimal