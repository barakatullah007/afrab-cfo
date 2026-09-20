from decimal import Decimal
from typing import Any


class SpendingAdvisor:
    """Analyzes spending patterns from existing category and budget data."""

    def analyze(
        self,
        *,
        category_insights: list[dict[str, Any]],
        monthly_cashflow: dict[str, Any],
        budget_utilization: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Return spending analysis and recommendations."""

        recommendations: list[str] = []
        flags: list[str] = []
        highest_category = None
        monthly_expense = self._decimal(
            monthly_cashflow.get("expense")
        )

        if category_insights:
            highest_category = category_insights[0]
            monthly_spent = self._decimal(
                highest_category.get("monthly_spent")
            )
            percentage = self._percentage(
                monthly_spent,
                monthly_expense,
            )

            recommendations.append(
                (
                    f"You spent {percentage:.2f}% of monthly expenses on "
                    f"{highest_category.get('category_name')}. Consider "
                    "reviewing this category first."
                )
            )

        exceeded_budgets = [
            budget
            for budget in budget_utilization
            if self._decimal(budget.get("utilization_percentage")) > 100
        ]

        for budget in exceeded_budgets:
            flags.append(
                f"{budget.get('category_name')} exceeded its budget."
            )

        if exceeded_budgets:
            recommendations.append(
                "Pause discretionary spending in over-budget categories."
            )

        if not category_insights:
            recommendations.append(
                "No spending transactions were found for the current month."
            )

        return {
            "highest_spending_category": highest_category,
            "overspending_flags": flags,
            "recurring_patterns": (
                "Recurring pattern detection requires historical recurring "
                "execution data, which is not available yet."
            ),
            "recommendations": recommendations,
        }

    def _percentage(
        self,
        numerator: Decimal,
        denominator: Decimal,
    ) -> Decimal:
        if denominator == 0:
            return Decimal("0")

        return (numerator / denominator) * Decimal("100")

    def _decimal(
        self,
        value: Any,
    ) -> Decimal:
        if value is None:
            return Decimal("0")

        return Decimal(str(value))
