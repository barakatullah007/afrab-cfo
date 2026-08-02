from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class DashboardRecentTransaction(BaseModel):

    id: int

    description: str

    merchant: str | None

    amount: Decimal

    transaction_date: datetime

    category_name: str

    category_icon: str

    category_color: str

    account_name: str

    account_icon: str