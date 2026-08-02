from decimal import Decimal

from pydantic import BaseModel

from app.enums.goal import GoalStatus


class FinancialIntelligenceSummary(BaseModel):

    net_worth: Decimal

    monthly_income: Decimal

    monthly_expense: Decimal

    monthly_cash_flow: Decimal

    savings_rate: Decimal

    active_goals: int

    completed_goals: int

    active_budgets: int

    active_recurring_transactions: int


class BudgetUtilizationInsight(BaseModel):

    budget_id: int

    category_id: int

    category_name: str

    budget_amount: Decimal

    spent_amount: Decimal

    remaining_amount: Decimal

    utilization_percentage: Decimal


class GoalProgressInsight(BaseModel):

    goal_id: int

    name: str

    target_amount: Decimal

    current_amount: Decimal

    remaining_amount: Decimal

    progress_percentage: Decimal

    status: GoalStatus


class CategoryInsight(BaseModel):

    category_id: int

    category_name: str

    monthly_spent: Decimal

    transaction_count: int


class MonthlyCashFlow(BaseModel):

    income: Decimal

    expense: Decimal

    cash_flow: Decimal
