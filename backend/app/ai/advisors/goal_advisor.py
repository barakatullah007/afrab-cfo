from decimal import Decimal
from typing import Any


class GoalAdvisor:
    """Analyzes active goals and recommends monthly contributions."""

    def analyze(
        self,
        goal_progress: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Return goal prioritization and contribution advice."""

        active_goals = [
            goal
            for goal in goal_progress
            if goal.get("status") == "active"
        ]

        prioritized_goals = sorted(
            active_goals,
            key=lambda goal: self._decimal(
                goal.get("remaining_amount")
            ),
            reverse=True,
        )

        contribution_plan = [
            {
                "goal_id": goal.get("goal_id"),
                "name": goal.get("name"),
                "remaining_amount": goal.get("remaining_amount"),
                "suggested_monthly_contribution": (
                    self._decimal(goal.get("remaining_amount")) / Decimal("12")
                ),
            }
            for goal in prioritized_goals
        ]

        recommendations = []

        if contribution_plan:
            recommendations.append(
                "Prioritize goals with the largest remaining amount and set a monthly contribution."
            )
        else:
            recommendations.append(
                "No active goals were found. Create a measurable goal to track progress."
            )

        return {
            "active_goals": active_goals,
            "prioritized_goals": prioritized_goals,
            "contribution_plan": contribution_plan,
            "recommendations": recommendations,
        }

    def _decimal(
        self,
        value: Any,
    ) -> Decimal:
        if value is None:
            return Decimal("0")

        return Decimal(str(value))
