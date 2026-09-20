class PersonalCFOPlanner:
    """Planner-ready agent facade for Personal CFO advisory intents."""

    def plan(
        self,
        intent: str,
    ) -> list[str]:
        """Return advisor/tool steps required for an intent."""

        plans = {
            "financial_health": [
                "financial_summary",
                "budget_utilization",
                "goal_progress",
                "cash_flow",
                "recurring_transactions",
                "financial_health_advisor",
            ],
            "spending_advice": [
                "category_insights",
                "budget_utilization",
                "spending_advisor",
            ],
            "budget_advice": [
                "budget_utilization",
                "budget_advisor",
            ],
            "goal_advice": [
                "goal_progress",
                "goal_advisor",
            ],
            "savings_advice": [
                "financial_summary",
                "cash_flow",
                "savings_advisor",
            ],
        }

        return plans.get(
            intent,
            [],
        )
