from decimal import Decimal
from typing import Any


class SavingsAdvisor:
    """Recommends savings actions from financial intelligence data."""

    def analyze(
        self,
        summary: dict[str, Any],
        monthly_cashflow: dict[str, Any],
    ) -> dict[str, Any]:
        """Return savings rate and monthly savings recommendations."""

        monthly_income = self._decimal(
            summary.get("monthly_income")
        )
        monthly_expense = self._decimal(
            summary.get("monthly_expense")
        )
        monthly_cash_flow = self._decimal(
            monthly_cashflow.get("cash_flow")
        )
        savings_rate = self._decimal(
            summary.get("savings_rate")
        )

        emergency_fund = monthly_expense * Decimal("6")
        target_monthly_savings = monthly_income * Decimal("0.20")
        suggested_monthly_savings = min(
            monthly_cash_flow,
            target_monthly_savings,
        )

        if suggested_monthly_savings < 0:
            suggested_monthly_savings = Decimal("0")

        recommendations = [
            "Build an emergency fund equal to six months of expenses.",
        ]

        if savings_rate < 20:
            recommendations.append(
                "Increase savings rate toward 20% of monthly income."
            )
        else:
            recommendations.append(
                "Savings rate is healthy. Keep saving consistently."
            )

        return {
            "savings_rate": savings_rate,
            "suggested_emergency_fund": emergency_fund,
            "suggested_monthly_savings": suggested_monthly_savings,
            "recommendations": recommendations,
        }

    def _decimal(
        self,
        value: Any,
    ) -> Decimal:
        if value is None:
            return Decimal("0")

        return Decimal(str(value))
