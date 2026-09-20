import unittest

from app.ai.planner import PersonalCFOAgentPlanner
from app.llm.schemas import LLMGenerationResult


class FakeFinancialService:
    def __init__(self):
        self.calls = {
            "summary": 0,
            "budget": 0,
            "goals": 0,
            "cashflow": 0,
            "categories": 0,
        }

    def get_summary(self, db, current_user):
        self.calls["summary"] += 1
        return {
            "monthly_income": 100000,
            "monthly_expense": 55000,
            "savings_rate": 45,
        }

    def get_budget_utilization(self, db, current_user):
        self.calls["budget"] += 1
        return [
            {
                "category_name": "Shopping",
                "spent_amount": 15000,
                "utilization_percentage": 75,
            }
        ]

    def get_goal_progress(self, db, current_user):
        self.calls["goals"] += 1
        return [
            {
                "goal_id": 1,
                "name": "Emergency fund",
                "status": "active",
                "remaining_amount": 60000,
                "progress_percentage": 50,
            }
        ]

    def get_monthly_cashflow(self, db, current_user):
        self.calls["cashflow"] += 1
        return {
            "income": 100000,
            "expense": 55000,
            "cash_flow": 45000,
        }

    def get_category_insights(self, db, current_user):
        self.calls["categories"] += 1
        return [
            {
                "category_name": "Food",
                "monthly_spent": 12000,
            }
        ]


class FakeRecurringService:
    def __init__(self):
        self.calls = 0

    def get_recurring_transactions(self, db, current_user):
        self.calls += 1
        return [
            {
                "amount": 10000,
                "is_active": True,
                "transaction_type": "expense",
            }
        ]


class FakeDashboardService:
    def get_summary(self, db, current_user):
        return {"balance": 1000}


class FakeAccountService:
    def get_accounts(self, db, current_user):
        return []


class FakeTransactionService:
    def get_transactions(self, db, current_user):
        return []


class FakeLLMService:
    def __init__(self):
        self.last_tool_output = None

    def generate_answer(self, *, user_message, tool_output, fallback_answer):
        self.last_tool_output = tool_output
        return LLMGenerationResult(
            answer=fallback_answer,
            provider="fake",
            model="fake-model",
            latency_ms=0,
        )


def build_planner():
    financial_service = FakeFinancialService()
    recurring_service = FakeRecurringService()
    llm_service = FakeLLMService()
    planner = PersonalCFOAgentPlanner(
        account_service=FakeAccountService(),
        dashboard_service=FakeDashboardService(),
        financial_service=financial_service,
        recurring_service=recurring_service,
        transaction_service=FakeTransactionService(),
        llm_service=llm_service,
    )
    return planner, financial_service, recurring_service, llm_service


class PersonalCFOPlannerSmokeTests(unittest.TestCase):
    def test_multi_tool_financial_planning(self):
        planner, _, _, llm_service = build_planner()

        result = planner.run(
            db=None,
            current_user=None,
            question="Am I financially healthy?",
        )

        context = result["context"]
        self.assertEqual(result["intent"], "financial_health")
        self.assertEqual(
            context.execution_order,
            [
                "financial_summary",
                "budget_utilization",
                "goal_progress",
                "monthly_cash_flow",
                "recurring_expenses",
                "financial_health_advisor",
            ],
        )
        self.assertIn("advisor_outputs", llm_service.last_tool_output)

    def test_goal_prioritization(self):
        planner, _, _, _ = build_planner()

        result = planner.run(
            db=None,
            current_user=None,
            question="Which goal should I prioritize?",
        )

        context = result["context"]
        self.assertEqual(result["intent"], "goal_prioritization")
        self.assertEqual(
            context.execution_order,
            [
                "goal_progress",
                "financial_summary",
                "monthly_cash_flow",
                "budget_utilization",
                "recurring_expenses",
                "savings_advisor",
                "financial_health_advisor",
            ],
        )

    def test_spending_reduction_advice(self):
        planner, _, _, _ = build_planner()

        result = planner.run(
            db=None,
            current_user=None,
            question="How can I reduce my spending?",
        )

        context = result["context"]
        self.assertEqual(result["intent"], "spending_reduction")
        self.assertEqual(
            context.execution_order,
            [
                "category_insights",
                "monthly_cash_flow",
                "budget_utilization",
                "spending_advisor",
                "budget_advisor",
            ],
        )

    def test_purchase_affordability_analysis(self):
        planner, _, _, _ = build_planner()

        result = planner.run(
            db=None,
            current_user=None,
            question="Can I buy a Rs 90,000 laptop next month?",
        )

        context = result["context"]
        self.assertEqual(result["intent"], "purchase_affordability")
        self.assertEqual(
            context.execution_order,
            [
                "financial_summary",
                "monthly_cash_flow",
                "recurring_expenses",
                "budget_utilization",
                "goal_progress",
                "financial_health_advisor",
            ],
        )

    def test_duplicate_tool_prevention(self):
        planner, financial_service, recurring_service, _ = build_planner()

        planner.run(
            db=None,
            current_user=None,
            question="Which goal should I prioritize?",
        )

        self.assertEqual(financial_service.calls["summary"], 1)
        self.assertEqual(financial_service.calls["budget"], 1)
        self.assertEqual(financial_service.calls["goals"], 1)
        self.assertEqual(financial_service.calls["cashflow"], 1)
        self.assertEqual(recurring_service.calls, 1)

    def test_unknown_question_handling(self):
        planner, _, _, _ = build_planner()

        result = planner.run(
            db=None,
            current_user=None,
            question="What is the weather tomorrow?",
        )

        context = result["context"]
        self.assertEqual(result["intent"], "unknown")
        self.assertEqual(context.execution_order, [])
        self.assertIsNone(result["tool_output"])


if __name__ == "__main__":
    unittest.main()
