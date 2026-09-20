import unittest

from app.ai.planner import PersonalCFOAgentPlanner
from app.ai.planner.planning_rules import PlanningRules
from app.llm.schemas import LLMGenerationResult
from app.rag.chunking import ChunkingConfig, TextChunker
from app.rag.document_loader import LoadedDocument
from app.rag.schemas import KnowledgeDocument, RetrievedChunk, SearchResult


class PlanningRulesRAGRoutingTests(unittest.TestCase):
    """Verify the planner routes to RAG only for education/hybrid questions."""

    def test_definitional_question_routes_to_financial_education(self):
        rule = PlanningRules.match("What is an emergency fund?")

        self.assertIsNotNone(rule)
        self.assertEqual(rule.goal, "financial_education")
        self.assertTrue(rule.use_rag)
        self.assertEqual(rule.tools, ())

    def test_fifty_thirty_twenty_routes_to_financial_education(self):
        rule = PlanningRules.match("How does the 50/30/20 rule work?")

        self.assertEqual(rule.goal, "financial_education")
        self.assertTrue(rule.use_rag)

    def test_hybrid_investment_question_combines_data_and_rag(self):
        rule = PlanningRules.match("Can I invest ₹5,000 every month?")

        self.assertEqual(rule.goal, "investment_capacity")
        self.assertTrue(rule.use_rag)
        self.assertIn("financial_summary", rule.tools)
        self.assertIn("monthly_cash_flow", rule.tools)
        self.assertIn("savings_advisor", rule.advisors)

    def test_personal_data_question_does_not_use_rag(self):
        rule = PlanningRules.match("What did I spend last month?")

        self.assertFalse(rule.use_rag)

    def test_savings_advice_question_does_not_use_rag(self):
        # Phrased as personalized advice, not a definition, so this should
        # stay on the existing savings_advisor path rather than RAG.
        rule = PlanningRules.match("How much should I save every month?")

        self.assertEqual(rule.goal, "savings_advice")
        self.assertFalse(rule.use_rag)


class TextChunkerTests(unittest.TestCase):
    """Chunking should respect configured size/overlap and keep page metadata."""

    def test_chunk_document_preserves_page_number(self):
        document = KnowledgeDocument(
            document_id="doc-1",
            document_name="sample.txt",
            source_path="sample.txt",
            file_type="txt",
        )
        loaded = LoadedDocument(
            document=document,
            pages=[(None, "a" * 1000)],
        )

        chunker = TextChunker(ChunkingConfig(chunk_size=400, chunk_overlap=100))
        chunks = chunker.chunk_document(loaded)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(c.document_id == "doc-1" for c in chunks))
        self.assertTrue(all(len(c.text) <= 400 for c in chunks))

    def test_short_text_produces_single_chunk(self):
        document = KnowledgeDocument(
            document_id="doc-2",
            document_name="short.md",
            source_path="short.md",
            file_type="md",
        )
        loaded = LoadedDocument(
            document=document,
            pages=[(1, "A short piece of financial guidance.")],
        )

        chunker = TextChunker(ChunkingConfig(chunk_size=800, chunk_overlap=150))
        chunks = chunker.chunk_document(loaded)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].page_number, 1)

    def test_invalid_overlap_raises(self):
        with self.assertRaises(ValueError):
            ChunkingConfig(chunk_size=100, chunk_overlap=100)


class FakeRAGPipeline:
    """Stub pipeline so the planner integration can be tested without
    downloading real embedding/cross-encoder models."""

    def __init__(self):
        self.search_calls: list[str] = []

    def search(self, question: str) -> SearchResult:
        self.search_calls.append(question)
        return SearchResult(
            query=question,
            chunks=[
                RetrievedChunk(
                    chunk_id="chunk-1",
                    document_name="budgeting_basics.md",
                    page_number=None,
                    text="The 50/30/20 rule splits income into needs, wants, and savings.",
                    retrieval_score=0.9,
                    rerank_score=0.95,
                )
            ],
            used_reranker=True,
        )


class FakeLLMService:
    def generate_answer(self, *, user_message, tool_output, fallback_answer):
        return LLMGenerationResult(
            answer=fallback_answer,
            provider="fake",
            model="fake-model",
            latency_ms=0,
        )


class FakeEmptyService:
    """Generic stand-in for services the RAG-only path never calls."""

    def __getattr__(self, name):
        def _unused(*args, **kwargs):
            raise AssertionError(
                f"{name} should not be called for a pure knowledge lookup"
            )

        return _unused


class PlannerRAGIntegrationTests(unittest.TestCase):
    def test_financial_education_question_calls_rag_pipeline(self):
        rag_pipeline = FakeRAGPipeline()
        planner = PersonalCFOAgentPlanner(
            account_service=FakeEmptyService(),
            dashboard_service=FakeEmptyService(),
            financial_service=FakeEmptyService(),
            recurring_service=FakeEmptyService(),
            transaction_service=FakeEmptyService(),
            llm_service=FakeLLMService(),
            rag_pipeline=rag_pipeline,
        )

        result = planner.run(
            db=None,
            current_user=None,
            question="What is an emergency fund?",
        )

        context = result["context"]
        self.assertEqual(result["intent"], "financial_education")
        self.assertEqual(
            rag_pipeline.search_calls, ["What is an emergency fund?"]
        )
        self.assertIn("financial_knowledge", context.tool_outputs)

        knowledge_output = context.tool_outputs["financial_knowledge"]
        self.assertTrue(knowledge_output["available"])
        self.assertEqual(
            knowledge_output["sources"][0]["document_name"],
            "budgeting_basics.md",
        )

    def test_rag_disabled_returns_unavailable_without_error(self):
        planner = PersonalCFOAgentPlanner(
            account_service=FakeEmptyService(),
            dashboard_service=FakeEmptyService(),
            financial_service=FakeEmptyService(),
            recurring_service=FakeEmptyService(),
            transaction_service=FakeEmptyService(),
            llm_service=FakeLLMService(),
            rag_pipeline=None,
        )

        result = planner.run(
            db=None,
            current_user=None,
            question="What is an index fund?",
        )

        context = result["context"]
        knowledge_output = context.tool_outputs["financial_knowledge"]
        self.assertFalse(knowledge_output["available"])
        self.assertEqual(knowledge_output["sources"], [])


if __name__ == "__main__":
    unittest.main()
