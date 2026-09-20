from decimal import Decimal
from typing import Any


class FinancialHealthAdvisor:
    """Scores the user's financial health from existing financial data."""

    def analyze(
        self,
        *,
        summary: dict[str, Any],
        budget_utilization: list[dict[str, Any]],
        goal_progress: list[dict[str, Any]],
        cash_flow: dict[str, Any],
        recurring_transactions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Return financial health score and recommendations.

        Args:
            summary: Financial intelligence summary.
            budget_utilization: Current month budget utilization.
            goal_progress: Goal progress insights.
            cash_flow: Monthly cashflow insight.
            recurring_transactions: Recurring transaction definitions.

        Returns:
            Financial health assessment.
        """

        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        score = (
            self._score_savings_rate(
                self._decimal(summary.get("savings_rate")),
                strengths,
                weaknesses,
                recommendations,
            )
            + self._score_budget_utilization(
                budget_utilization,
                strengths,
                weaknesses,
                recommendations,
            )
            + self._score_goal_progress(
                goal_progress,
                strengths,
                weaknesses,
                recommendations,
            )
            + self._score_cash_flow(
                self._decimal(cash_flow.get("cash_flow")),
                strengths,
                weaknesses,
                recommendations,
            )
            + self._score_recurring_expenses(
                summary,
                recurring_transactions,
                strengths,
                weaknesses,
                recommendations,
            )
        )

        score = max(
            0,
            min(
                100,
                int(score),
            ),
        )

        return {
            "score": score,
            "grade": self._grade(score),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
        }

    def _score_savings_rate(
        self,
        savings_rate: Decimal,
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> int:
        if savings_rate >= 20:
            strengths.append("Savings rate is at or above 20%.")
            return 25

        if savings_rate > 0:
            weaknesses.append("Savings rate is positive but below 20%.")
            recommendations.append("Aim to move savings rate toward 20%.")
            return 14

        weaknesses.append("Savings rate is zero or negative.")
        recommendations.append("Reduce expenses or increase income to create savings.")
        return 0

    def _score_budget_utilization(
        self,
        budgets: list[dict[str, Any]],
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> int:
        if not budgets:
            weaknesses.append("No active budgets are available for this month.")
            recommendations.append("Create budgets for major expense categories.")
            return 8

        average_utilization = sum(
            self._decimal(budget.get("utilization_percentage"))
            for budget in budgets
        ) / Decimal(len(budgets))

        if average_utilization <= 80:
            strengths.append("Average budget utilization is below 80%.")
            return 20

        if average_utilization <= 100:
            weaknesses.append("Budgets are close to their monthly limits.")
            recommendations.append("Review categories above 80% utilization.")
            return 10

        weaknesses.append("Average budget utilization exceeds 100%.")
        recommendations.append("Reduce spending in over-budget categories.")
        return 0

    def _score_goal_progress(
        self,
        goals: list[dict[str, Any]],
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> int:
        if not goals:
            weaknesses.append("No active goals are being tracked.")
            recommendations.append("Create at least one measurable financial goal.")
            return 5

        average_progress = sum(
            self._decimal(goal.get("progress_percentage"))
            for goal in goals
        ) / Decimal(len(goals))

        if average_progress >= 50:
            strengths.append("Goal progress is above 50% on average.")
            return 15

        weaknesses.append("Goal progress is below 50% on average.")
        recommendations.append("Assign a monthly contribution to priority goals.")
        return 8

    def _score_cash_flow(
        self,
        monthly_cash_flow: Decimal,
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> int:
        if monthly_cash_flow > 0:
            strengths.append("Monthly cash flow is positive.")
            return 20

        if monthly_cash_flow == 0:
            weaknesses.append("Monthly cash flow is break-even.")
            recommendations.append("Create a small monthly surplus.")
            return 10

        weaknesses.append("Monthly cash flow is negative.")
        recommendations.append("Reduce variable expenses immediately.")
        return 0

    def _score_recurring_expenses(
        self,
        summary: dict[str, Any],
        recurring_transactions: list[dict[str, Any]],
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> int:
        monthly_income = self._decimal(summary.get("monthly_income"))
        recurring_expense_total = sum(
            self._decimal(item.get("amount"))
            for item in recurring_transactions
            if item.get("is_active") is True
            and item.get("transaction_type") == "expense"
        )

        if recurring_expense_total == 0:
            strengths.append("No active recurring expenses are recorded.")
            return 20

        if monthly_income == 0:
            weaknesses.append("Recurring expenses exist but monthly income is zero.")
            recommendations.append("Review recurring obligations against income.")
            return 5

        recurring_ratio = (recurring_expense_total / monthly_income) * 100

        if recurring_ratio <= 30:
            strengths.append("Recurring expenses are below 30% of monthly income.")
            return 20

        if recurring_ratio <= 50:
            weaknesses.append("Recurring expenses are above 30% of monthly income.")
            recommendations.append("Audit subscriptions, EMIs, and fixed bills.")
            return 10

        weaknesses.append("Recurring expenses are above 50% of monthly income.")
        recommendations.append("Renegotiate or reduce recurring commitments.")
        return 0

    def _grade(
        self,
        score: int,
    ) -> str:
        if score >= 90:
            return "A"
        if score >= 75:
            return "B"
        if score >= 60:
            return "C"
        if score >= 45:
            return "D"
        return "F"

    def _decimal(
        self,
        value: Any,
    ) -> Decimal:
        if value is None:
            return Decimal("0")

        return Decimal(str(value))
