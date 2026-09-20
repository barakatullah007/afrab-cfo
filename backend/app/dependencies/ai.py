from fastapi import Depends

from app.dependencies.services import (
    get_account_service,
    get_dashboard_service,
    get_financial_intelligence_service,
    get_recurring_transaction_service,
    get_transaction_service,
)
from app.llm.service import LLMService
from app.rag.pipeline import RAGPipeline
from app.services.account_service import AccountService
from app.services.ai_conversation_service import AIConversationService
from app.services.dashboard_service import DashboardService
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService,
)
from app.services.recurring_transaction_service import (
    RecurringTransactionService,
)
from app.services.transaction_service import TransactionService


def get_llm_service() -> LLMService:
    return LLMService()


_rag_pipeline: RAGPipeline | None = None


def get_rag_pipeline() -> RAGPipeline:
    """Return a process-wide singleton RAGPipeline.

    A singleton is used so the embedding model, cross-encoder, and FAISS
    index are loaded once per process rather than per-request.
    """

    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline


def get_ai_conversation_service(
    account_service: AccountService = Depends(get_account_service),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    financial_service: FinancialIntelligenceService = Depends(
        get_financial_intelligence_service
    ),
    recurring_service: RecurringTransactionService = Depends(
        get_recurring_transaction_service
    ),
    transaction_service: TransactionService = Depends(
        get_transaction_service
    ),
    llm_service: LLMService = Depends(get_llm_service),
    rag_pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> AIConversationService:
    return AIConversationService(
        account_service=account_service,
        dashboard_service=dashboard_service,
        financial_service=financial_service,
        recurring_service=recurring_service,
        transaction_service=transaction_service,
        llm_service=llm_service,
        rag_pipeline=rag_pipeline,
    )
