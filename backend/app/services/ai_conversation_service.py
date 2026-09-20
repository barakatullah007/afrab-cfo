from typing import Any

from sqlalchemy.orm import Session

from app.ai.prompts.system_prompt import SYSTEM_PROMPT
from app.ai.planner import PersonalCFOAgentPlanner
from app.ai.tools import (
    account_tools,
    advisor_tools,
    dashboard_tools,
    financial_tools,
    transaction_tools,
)
from app.llm.service import LLMService
from app.models.user import User
from app.schemas.ai import AIChatRequest, AIChatResponse, Confidence
from app.services.account_service import AccountService
from app.services.dashboard_service import DashboardService
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService,
)
from app.services.recurring_transaction_service import (
    RecurringTransactionService,
)
from app.services.transaction_service import TransactionService
from app.services.conversation_memory_service import ConversationMemoryService
from app.ai.memory.memory_manager import MemoryManager
from app.rag.pipeline import RAGPipeline


class AIConversationService:
    """AI conversation pipeline with deterministic routing.

    This service detects intent, dispatches to the existing AI tool layer,
    and asks the configured LLM to explain the resulting tool output.
    """

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
        self.planner = PersonalCFOAgentPlanner(
            account_service=account_service,
            dashboard_service=dashboard_service,
            financial_service=financial_service,
            recurring_service=recurring_service,
            transaction_service=transaction_service,
            llm_service=llm_service,
            rag_pipeline=rag_pipeline,
        )
        self.system_prompt = SYSTEM_PROMPT
        # Memory manager for storing and retrieving conversation memory
        self.memory_service = ConversationMemoryService()
        self.memory_manager = MemoryManager(self.memory_service)

    def chat(
        self,
        db: Session,
        current_user: User,
        request: AIChatRequest,
    ) -> AIChatResponse:
        """Handle a deterministic chat request.

        Args:
            db: Database session.
            current_user: Authenticated user.
            request: Chat request payload.

        Returns:
            Structured AI chat response.
        """

        # Record the incoming user message to memory (best-effort)
        try:
            self.memory_manager.record_message(
                db,
                current_user.id,
                role="user",
                message=request.message,
                memory_type="short_term",
            )
        except Exception:
            # best-effort: don't fail the conversation on memory errors
            pass

        result = self.planner.run(
            db=db,
            current_user=current_user,
            question=request.message,
        )
        context = result["context"]
        knowledge_output = context.tool_outputs.get("financial_knowledge", {})

        response = AIChatResponse(
            intent=result["intent"],
            tool_used=result["tool_used"],
            answer=result["answer"],
            tool_output=result["tool_output"],
            confidence=result["confidence"],
            provider=result["provider"],
            model=result["model"],
            planning_steps=context.execution_order,
            tools_executed=list(context.executed_tools),
            advisors_used=list(context.advisor_outputs.keys()),
            execution_time_ms=context.execution_time_ms(),
            sources=knowledge_output.get("sources", []),
        )

        # Record assistant response and attempt to compact long histories (best-effort)
        try:
            assistant_text = result.get("answer") or ""
            self.memory_manager.record_message(
                db,
                current_user.id,
                role="assistant",
                message=assistant_text,
                memory_type="short_term",
            )
            try:
                self.memory_manager.summarize_and_compact(db, current_user.id, threshold=200)
            except Exception:
                pass
        except Exception:
            pass

        return response

    def _detect_intent(
        self,
        message: str,
    ) -> tuple[str, Confidence]:
        normalized = message.lower().strip()

        if self._contains_any(
            normalized,
            [
                "financially healthy",
                "financial health",
                "health score",
                "am i healthy",
            ],
        ):
            return (
                "financial_health",
                "high",
            )

        if self._contains_any(
            normalized,
            [
                "improve my savings",
                "how much should i save",
                "save every month",
                "savings advice",
                "emergency fund",
            ],
        ):
            return (
                "savings_advice",
                "high",
            )

        if self._contains_any(
            normalized,
            [
                "what should i reduce",
                "why am i overspending",
                "overspending",
                "reduce spending",
                "spending advice",
            ],
        ):
            return (
                "spending_advice",
                "high",
            )

        if self._contains_any(
            normalized,
            [
                "which goal should i prioritize",
                "goal should i prioritize",
                "prioritize goal",
                "goal advice",
            ],
        ):
            return (
                "goal_advice",
                "high",
            )

        if self._contains_any(
            normalized,
            [
                "budget advice",
                "budget recommendation",
                "budget recommendations",
            ],
        ):
            return (
                "budget_advice",
                "high",
            )

        if self._contains_any(
            normalized,
            [
                "help",
                "what can you do",
                "how can you help",
            ],
        ):
            return (
                "help",
                "high",
            )

        if self._contains_any(
            normalized,
            [
                "budget",
                "utilization",
                "budget usage",
            ],
        ):
            return (
                "budget_utilization",
                "high",
            )

        if self._contains_any(
            normalized,
            [
                "goal",
                "goals",
                "progress",
            ],
        ):
            return (
                "goal_progress",
                "high",
            )

        if self._contains_any(
            normalized,
            [
                "cash flow",
                "cashflow",
            ],
        ):
            return (
                "cash_flow",
                "high",
            )

        if self._contains_any(
            normalized,
            [
                "spend",
                "spent",
                "category",
                "food",
                "shopping",
                "expense category",
            ],
        ):
            return (
                "category_insights",
                "medium",
            )

        if self._contains_any(
            normalized,
            [
                "dashboard",
                "recent",
                "snapshot",
            ],
        ):
            return (
                "dashboard",
                "high",
            )

        if self._contains_any(
            normalized,
            [
                "account",
                "accounts",
                "balance",
            ],
        ):
            return (
                "accounts",
                "high",
            )

        if self._contains_any(
            normalized,
            [
                "transaction",
                "transactions",
            ],
        ):
            return (
                "transactions",
                "high",
            )

        if self._contains_any(
            normalized,
            [
                "summary",
                "overview",
                "net worth",
                "savings rate",
                "income",
                "expense",
            ],
        ):
            return (
                "financial_summary",
                "high",
            )

        return (
            "unknown",
            "low",
        )

    def _dispatch_tool(
        self,
        intent: str,
        db: Session,
        current_user: User,
    ) -> tuple[str, Any]:
        self.planner.plan(
            intent,
        )

        if intent == "financial_health":
            return (
                "advisor_tools.get_financial_health",
                advisor_tools.get_financial_health(
                    db,
                    current_user,
                    self.financial_service,
                    self.recurring_service,
                ),
            )

        if intent == "spending_advice":
            return (
                "advisor_tools.get_spending_analysis",
                advisor_tools.get_spending_analysis(
                    db,
                    current_user,
                    self.financial_service,
                ),
            )

        if intent == "budget_advice":
            return (
                "advisor_tools.get_budget_advice",
                advisor_tools.get_budget_advice(
                    db,
                    current_user,
                    self.financial_service,
                ),
            )

        if intent == "goal_advice":
            return (
                "advisor_tools.get_goal_advice",
                advisor_tools.get_goal_advice(
                    db,
                    current_user,
                    self.financial_service,
                ),
            )

        if intent == "savings_advice":
            return (
                "advisor_tools.get_savings_advice",
                advisor_tools.get_savings_advice(
                    db,
                    current_user,
                    self.financial_service,
                ),
            )

        if intent == "financial_summary":
            return (
                "financial_tools.get_financial_summary",
                financial_tools.get_financial_summary(
                    db,
                    current_user,
                    self.financial_service,
                ),
            )

        if intent == "budget_utilization":
            return (
                "financial_tools.get_budget_utilization",
                financial_tools.get_budget_utilization(
                    db,
                    current_user,
                    self.financial_service,
                ),
            )

        if intent == "goal_progress":
            return (
                "financial_tools.get_goal_progress",
                financial_tools.get_goal_progress(
                    db,
                    current_user,
                    self.financial_service,
                ),
            )

        if intent == "cash_flow":
            return (
                "financial_tools.get_monthly_cashflow",
                financial_tools.get_monthly_cashflow(
                    db,
                    current_user,
                    self.financial_service,
                ),
            )

        if intent == "category_insights":
            return (
                "financial_tools.get_category_insights",
                financial_tools.get_category_insights(
                    db,
                    current_user,
                    self.financial_service,
                ),
            )

        if intent == "dashboard":
            return (
                "dashboard_tools.get_dashboard_summary",
                dashboard_tools.get_dashboard_summary(
                    db,
                    current_user,
                    self.dashboard_service,
                ),
            )

        if intent == "accounts":
            return (
                "account_tools.get_accounts",
                account_tools.get_accounts(
                    db,
                    current_user,
                    self.account_service,
                ),
            )

        return (
            "transaction_tools.get_transactions",
            transaction_tools.get_transactions(
                db,
                current_user,
                self.transaction_service,
            ),
        )

    def _build_answer(
        self,
        intent: str,
        tool_output: Any,
    ) -> str:
        if intent == "financial_summary":
            return "Here is your current financial summary."

        if intent == "financial_health":
            return "Here is your financial health assessment."

        if intent == "spending_advice":
            return "Here is your spending analysis and reduction advice."

        if intent == "budget_advice":
            return "Here is your budget advice."

        if intent == "goal_advice":
            return "Here is your goal prioritization advice."

        if intent == "savings_advice":
            return "Here is your savings advice."

        if intent == "budget_utilization":
            return "Here is your budget utilization for the current month."

        if intent == "goal_progress":
            return "Here is your current goal progress."

        if intent == "cash_flow":
            return "Here is your current monthly cash flow."

        if intent == "category_insights":
            return "Here is your current month spending by category."

        if intent == "dashboard":
            return "Here is your dashboard snapshot."

        if intent == "accounts":
            return "Here are your accounts."

        return "Here are your recent transactions."

    def _contains_any(
        self,
        value: str,
        keywords: list[str],
    ) -> bool:
        return any(
            keyword in value
            for keyword in keywords
        )
