from __future__ import annotations

import logging
import time
from typing import Any

from sqlalchemy.orm import Session

from app.ai.advisors.budget_advisor import BudgetAdvisor
from app.ai.advisors.financial_health_advisor import FinancialHealthAdvisor
from app.ai.advisors.savings_advisor import SavingsAdvisor
from app.ai.advisors.spending_advisor import SpendingAdvisor
from app.ai.planner.execution_context import PlannerExecutionContext
from app.ai.planner.planning_rules import PlanningRule, PlanningRules
from app.ai.tools import (
    account_tools,
    dashboard_tools,
    financial_tools,
    knowledge_tools,
    recurring_tools,
    transaction_tools,
)
from app.ai.tools._serialization import to_jsonable
from app.llm.service import LLMService
from app.llm.schemas import LLMGenerationResult
from app.models.user import User
from app.rag.pipeline import RAGPipeline
from app.services.account_service import AccountService
from app.services.dashboard_service import DashboardService
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService,
)
from app.services.recurring_transaction_service import (
    RecurringTransactionService,
)
from app.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)


class PersonalCFOAgentPlanner:
    """Executes reusable planning rules against the existing tool layer."""

    def __init__(
        self,
        *,
        account_service: AccountService,
        dashboard_service: DashboardService,
        financial_service: FinancialIntelligenceService,
        recurring_service: RecurringTransactionService,
        transaction_service: TransactionService,
        llm_service: LLMService,
        rag_pipeline: RAGPipeline | None = None,
    ):
        self.account_service = account_service
        self.dashboard_service = dashboard_service
        self.financial_service = financial_service
        self.recurring_service = recurring_service
        self.transaction_service = transaction_service
        self.llm_service = llm_service
        self.rag_pipeline = rag_pipeline

    def plan(
        self,
        question: str,
    ) -> tuple[PlanningRule | None, str]:
        rule = PlanningRules.match(question)

        if rule is None:
            return None, "low"

        return rule, rule.confidence

    def run(
        self,
        *,
        db: Session,
        current_user: User,
        question: str,
    ) -> dict[str, Any]:
        planning_started = time.perf_counter()
        rule, confidence = self.plan(question)

        if rule is None:
            context = PlannerExecutionContext(
                user_question=question,
                detected_goal="unknown",
            )
            return {
                "intent": "unknown",
                "confidence": confidence,
                "answer": (
                    "I couldn't determine what financial information you're "
                    "looking for. Could you rephrase your question?"
                ),
                "tool_used": None,
                "tool_output": None,
                "provider": None,
                "model": None,
                "context": context,
            }

        if rule.goal == "help":
            context = PlannerExecutionContext(
                user_question=question,
                detected_goal=rule.goal,
            )
            return {
                "intent": rule.goal,
                "confidence": confidence,
                "answer": (
                    "I can help with financial summaries, budgets, goals, "
                    "cash flow, spending categories, accounts, transactions, "
                    "and dashboard snapshots."
                ),
                "tool_used": None,
                "tool_output": None,
                "provider": None,
                "model": None,
                "context": context,
            }

        context = PlannerExecutionContext(
            user_question=question,
            detected_goal=rule.goal,
        )

        logger.info(
            "planner_decision goal=%s tools=%s advisors=%s",
            rule.goal,
            list(rule.tools),
            list(rule.advisors),
        )

        for tool_name in rule.tools:
            self._execute_tool(
                tool_name,
                db,
                current_user,
                context,
            )

        for advisor_name in rule.advisors:
            self._execute_advisor(
                advisor_name,
                context,
            )

        if rule.use_rag:
            self._execute_knowledge_search(
                question,
                context,
            )

        fallback_answer = self._build_fallback_answer(rule.goal)
        llm_started = time.perf_counter()
        llm_result = self.llm_service.generate_answer(
            user_message=question,
            tool_output=context.to_llm_payload(),
            fallback_answer=fallback_answer,
        )
        context.llm_latency_ms = int(
            (time.perf_counter() - llm_started) * 1000
        )

        total_ms = int(
            (time.perf_counter() - planning_started) * 1000
        )
        logger.info(
            "planner_complete goal=%s execution_order=%s llm_latency_ms=%s total_ms=%s",
            rule.goal,
            context.execution_order,
            context.llm_latency_ms,
            total_ms,
        )

        return {
            "intent": rule.goal,
            "confidence": confidence,
            "answer": llm_result.answer,
            "tool_used": "personal_cfo_planner",
            "tool_output": context.to_llm_payload(),
            "provider": llm_result.provider,
            "model": llm_result.model,
            "context": context,
        }

    def _execute_tool(
        self,
        tool_name: str,
        db: Session,
        current_user: User,
        context: PlannerExecutionContext,
    ) -> Any:
        if context.has_tool_output(tool_name):
            logger.info("planner_skip_duplicate_tool tool=%s", tool_name)
            return context.tool_outputs[tool_name]

        logger.info("planner_execute_tool tool=%s", tool_name)

        tool_output = self._tool_registry(
            db,
            current_user,
        )[tool_name]()
        context.add_tool_output(
            tool_name,
            tool_output,
        )

        return tool_output

    def _execute_advisor(
        self,
        advisor_name: str,
        context: PlannerExecutionContext,
    ) -> Any:
        logger.info("planner_execute_advisor advisor=%s", advisor_name)
        advisor_output = self._advisor_registry(context)[advisor_name]()
        advisor_output = to_jsonable(advisor_output)
        context.add_advisor_output(
            advisor_name,
            advisor_output,
        )
        return advisor_output

    def _execute_knowledge_search(
        self,
        question: str,
        context: PlannerExecutionContext,
    ) -> dict[str, Any]:
        if context.has_tool_output("financial_knowledge"):
            return context.tool_outputs["financial_knowledge"]

        logger.info("planner_execute_tool tool=financial_knowledge")

        knowledge_output = knowledge_tools.search_financial_knowledge(
            question,
            self.rag_pipeline,
        )
        context.add_tool_output(
            "financial_knowledge",
            knowledge_output,
        )

        return knowledge_output

    def _tool_registry(
        self,
        db: Session,
        current_user: User,
    ) -> dict[str, Any]:
        return {
            "financial_summary": lambda: financial_tools.get_financial_summary(
                db,
                current_user,
                self.financial_service,
            ),
            "budget_utilization": lambda: financial_tools.get_budget_utilization(
                db,
                current_user,
                self.financial_service,
            ),
            "goal_progress": lambda: financial_tools.get_goal_progress(
                db,
                current_user,
                self.financial_service,
            ),
            "category_insights": lambda: financial_tools.get_category_insights(
                db,
                current_user,
                self.financial_service,
            ),
            "monthly_cash_flow": lambda: financial_tools.get_monthly_cashflow(
                db,
                current_user,
                self.financial_service,
            ),
            "recurring_expenses": lambda: recurring_tools.get_recurring_transactions(
                db,
                current_user,
                self.recurring_service,
            ),
            "dashboard_summary": lambda: dashboard_tools.get_dashboard_summary(
                db,
                current_user,
                self.dashboard_service,
            ),
            "accounts": lambda: account_tools.get_accounts(
                db,
                current_user,
                self.account_service,
            ),
            "transactions": lambda: transaction_tools.get_transactions(
                db,
                current_user,
                self.transaction_service,
            ),
        }

    def _advisor_registry(
        self,
        context: PlannerExecutionContext,
    ) -> dict[str, Any]:
        return {
            "financial_health_advisor": lambda: FinancialHealthAdvisor().analyze(
                summary=context.tool_outputs.get("financial_summary", {}),
                budget_utilization=context.tool_outputs.get(
                    "budget_utilization",
                    [],
                ),
                goal_progress=context.tool_outputs.get("goal_progress", []),
                cash_flow=context.tool_outputs.get("monthly_cash_flow", {}),
                recurring_transactions=context.tool_outputs.get(
                    "recurring_expenses",
                    [],
                ),
            ),
            "spending_advisor": lambda: SpendingAdvisor().analyze(
                category_insights=context.tool_outputs.get(
                    "category_insights",
                    [],
                ),
                monthly_cashflow=context.tool_outputs.get(
                    "monthly_cash_flow",
                    {},
                ),
                budget_utilization=context.tool_outputs.get(
                    "budget_utilization",
                    [],
                ),
            ),
            "budget_advisor": lambda: BudgetAdvisor().analyze(
                context.tool_outputs.get(
                    "budget_utilization",
                    [],
                )
            ),
            "savings_advisor": lambda: SavingsAdvisor().analyze(
                summary=context.tool_outputs.get("financial_summary", {}),
                monthly_cashflow=context.tool_outputs.get(
                    "monthly_cash_flow",
                    {},
                ),
            ),
        }

    def _build_fallback_answer(
        self,
        goal: str,
    ) -> str:
        answers = {
            "financial_education": (
                "Here is what I found in the financial knowledge base."
            ),
            "investment_capacity": (
                "Here is an assessment based on your cash flow and "
                "relevant financial guidance."
            ),
            "purchase_affordability": (
                "Here is your purchase affordability analysis based on your "
                "current financial context."
            ),
            "goal_prioritization": (
                "Here is your goal prioritization analysis."
            ),
            "spending_reduction": (
                "Here is your spending reduction analysis."
            ),
            "financial_health": "Here is your financial health assessment.",
            "savings_advice": "Here is your savings advice.",
            "budget_advice": "Here is your budget advice.",
            "budget_utilization": (
                "Here is your budget utilization for the current month."
            ),
            "goal_progress": "Here is your current goal progress.",
            "cash_flow": "Here is your current monthly cash flow.",
            "category_insights": (
                "Here is your current month spending by category."
            ),
            "dashboard": "Here is your dashboard snapshot.",
            "accounts": "Here are your accounts.",
            "transactions": "Here are your recent transactions.",
            "financial_summary": "Here is your current financial summary.",
        }

        return answers.get(
            goal,
            "Here is the financial context I found.",
        )
