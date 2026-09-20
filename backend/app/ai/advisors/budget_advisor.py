from decimal import Decimal
from typing import Any


class BudgetAdvisor:
    """Analyzes budget utilization and recommends actions."""

    def analyze(
        self,
        budget_utilization: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Return budget advice based on current month utilization."""

        close_to_limit = []
        exceeded = []
        unused = []
        recommendations = []

        for budget in budget_utilization:
            utilization = self._decimal(
                budget.get("utilization_percentage")
            )

            if utilization > 100:
                exceeded.append(budget)
            elif utilization >= 80:
                close_to_limit.append(budget)
            elif self._decimal(budget.get("spent_amount")) == 0:
                unused.append(budget)

        if exceeded:
            recommendations.append(
                "Reduce or pause spending in exceeded budget categories."
            )

        if close_to_limit:
            recommendations.append(
                "Monitor categories that are above 80% utilization."
            )

        if unused:
            recommendations.append(
                "Review unused budgets and reallocate if they are no longer needed."
            )

        if not budget_utilization:
            recommendations.append(
                "Create budgets for your largest monthly expense categories."
            )

        return {
            "close_to_limit": close_to_limit,
            "exceeded": exceeded,
            "unused": unused,
            "recommendations": recommendations,
        }

    def _decimal(
        self,
        value: Any,
    ) -> Decimal:
        if value is None:
            return Decimal("0")

        return Decimal(str(value))
