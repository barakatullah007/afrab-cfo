from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanningRule:
    goal: str
    patterns: tuple[str, ...]
    tools: tuple[str, ...]
    advisors: tuple[str, ...] = ()
    confidence: str = "high"
    use_rag: bool = False

    def matches(
        self,
        normalized_question: str,
    ) -> bool:
        return any(
            pattern in normalized_question
            for pattern in self.patterns
        )


class PlanningRules:
    """Reusable rules that map question patterns to planner steps."""

    _RULES = (
        PlanningRule(
            goal="financial_education",
            patterns=(
                "50/30/20",
                "what is an emergency fund",
                "what is emergency fund",
                "how do sips work",
                "how does sip work",
                "what is a sip",
                "what is sip",
                "what is an index fund",
                "what is index fund",
                "what is a credit score",
                "what is credit score",
                "what is a mutual fund",
                "what is mutual fund",
                "what is diversification",
                "what is compound interest",
                "what is compounding",
                "how does compounding work",
                "what is inflation",
                "what is a stock",
                "what is an etf",
            ),
            tools=(),
            use_rag=True,
        ),
        PlanningRule(
            goal="investment_capacity",
            patterns=(
                "can i invest",
                "should i invest",
                "invest every month",
                "invest per month",
                "start a sip",
                "start sip",
                "invest in a sip",
            ),
            tools=(
                "financial_summary",
                "monthly_cash_flow",
            ),
            advisors=("savings_advisor",),
            use_rag=True,
        ),
        PlanningRule(
            goal="purchase_affordability",
            patterns=(
                "can i buy",
                "can i afford",
                "afford",
                "purchase",
                "buy a",
                "buy an",
            ),
            tools=(
                "financial_summary",
                "monthly_cash_flow",
                "recurring_expenses",
                "budget_utilization",
                "goal_progress",
            ),
            advisors=("financial_health_advisor",),
        ),
        PlanningRule(
            goal="goal_prioritization",
            patterns=(
                "which goal should i prioritize",
                "goal should i prioritize",
                "prioritize goal",
                "prioritize goals",
                "goal advice",
            ),
            tools=(
                "goal_progress",
                "financial_summary",
                "monthly_cash_flow",
                "budget_utilization",
                "recurring_expenses",
            ),
            advisors=(
                "savings_advisor",
                "financial_health_advisor",
            ),
        ),
        PlanningRule(
            goal="spending_reduction",
            patterns=(
                "how can i reduce my spending",
                "what should i reduce",
                "why am i overspending",
                "overspending",
                "reduce spending",
                "spending advice",
                "cut spending",
            ),
            tools=(
                "category_insights",
                "monthly_cash_flow",
                "budget_utilization",
            ),
            advisors=(
                "spending_advisor",
                "budget_advisor",
            ),
        ),
        PlanningRule(
            goal="financial_health",
            patterns=(
                "financially healthy",
                "financial health",
                "health score",
                "am i healthy",
            ),
            tools=(
                "financial_summary",
                "budget_utilization",
                "goal_progress",
                "monthly_cash_flow",
                "recurring_expenses",
            ),
            advisors=("financial_health_advisor",),
        ),
        PlanningRule(
            goal="savings_advice",
            patterns=(
                "improve my savings",
                "how much should i save",
                "save every month",
                "savings advice",
                "emergency fund",
            ),
            tools=(
                "financial_summary",
                "monthly_cash_flow",
            ),
            advisors=("savings_advisor",),
        ),
        PlanningRule(
            goal="budget_advice",
            patterns=(
                "budget advice",
                "budget recommendation",
                "budget recommendations",
            ),
            tools=("budget_utilization",),
            advisors=("budget_advisor",),
        ),
        PlanningRule(
            goal="budget_utilization",
            patterns=(
                "budget",
                "utilization",
                "budget usage",
            ),
            tools=("budget_utilization",),
            confidence="high",
        ),
        PlanningRule(
            goal="goal_progress",
            patterns=(
                "goal",
                "goals",
                "progress",
            ),
            tools=("goal_progress",),
        ),
        PlanningRule(
            goal="cash_flow",
            patterns=(
                "cash flow",
                "cashflow",
            ),
            tools=("monthly_cash_flow",),
        ),
        PlanningRule(
            goal="category_insights",
            patterns=(
                "spend",
                "spent",
                "category",
                "food",
                "shopping",
                "expense category",
            ),
            tools=("category_insights",),
            confidence="medium",
        ),
        PlanningRule(
            goal="dashboard",
            patterns=(
                "dashboard",
                "recent",
                "snapshot",
            ),
            tools=("dashboard_summary",),
        ),
        PlanningRule(
            goal="accounts",
            patterns=(
                "account",
                "accounts",
                "balance",
            ),
            tools=("accounts",),
        ),
        PlanningRule(
            goal="transactions",
            patterns=(
                "transaction",
                "transactions",
            ),
            tools=("transactions",),
        ),
        PlanningRule(
            goal="financial_summary",
            patterns=(
                "summary",
                "overview",
                "net worth",
                "savings rate",
                "income",
                "expense",
            ),
            tools=("financial_summary",),
        ),
    )

    @classmethod
    def match(
        cls,
        question: str,
    ) -> PlanningRule | None:
        normalized = question.lower().strip()

        if any(
            pattern in normalized
            for pattern in (
                "help",
                "what can you do",
                "how can you help",
            )
        ):
            return PlanningRule(
                goal="help",
                patterns=(),
                tools=(),
            )

        for rule in cls._RULES:
            if rule.matches(normalized):
                return rule

        return None
