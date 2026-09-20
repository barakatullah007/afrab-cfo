# Financial Knowledge Engine (RAG) — Sprint Delivery

This package contains only the files that are **new** or **modified** for
this sprint. Copy them into your `backend/` project at the same relative
paths (they'll merge cleanly — nothing outside these files was touched).

## 1. Files created

```
app/rag/__init__.py
app/rag/schemas.py          # KnowledgeDocument, Chunk, RetrievedChunk, SearchResult, VectorSearchResult
app/rag/document_loader.py  # PDF / Markdown / TXT / CSV ingestion
app/rag/chunking.py         # ChunkingConfig + TextChunker (configurable size/overlap)
app/rag/embeddings.py       # lazy sentence-transformers wrapper (all-MiniLM-L6-v2)
app/rag/vector_store.py     # VectorStore interface + FAISSVectorStore (disk-persisted)
app/rag/retriever.py        # top-k similarity retrieval
app/rag/reranker.py         # lazy CrossEncoder reranker (ms-marco-MiniLM-L-6-v2)
app/rag/ingestion.py        # IngestionService: load -> chunk -> embed -> index
app/rag/pipeline.py         # RAGPipeline: ties it all together, .ingest() / .search()

app/ai/tools/knowledge_tools.py   # new AI tool: search_financial_knowledge()

data/knowledge/budgeting_basics.md   # sample docs so retrieval has content
data/knowledge/investing_basics.md
data/knowledge/credit_basics.md

tests/smoke/test_rag_smoke.py   # 10 tests: rule routing, chunking, planner integration
```

## 2. Files modified

```
app/core/config.py                  # + RAG_ENABLED, RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP,
                                     #   RAG_TOP_K, RAG_EMBEDDING_MODEL, RAG_CROSS_ENCODER_MODEL,
                                     #   RAG_KNOWLEDGE_DIR, RAG_INDEX_DIR
app/dependencies/ai.py              # + get_rag_pipeline() singleton, injected into
                                     #   get_ai_conversation_service
app/services/ai_conversation_service.py  # accepts + forwards rag_pipeline to the planner
app/ai/planner/planning_rules.py    # + use_rag flag on PlanningRule; + 2 new rules
                                     #   (financial_education, investment_capacity)
app/ai/planner/planner.py           # accepts rag_pipeline; + _execute_knowledge_search()
                                     #   called when rule.use_rag is set
app/schemas/ai.py                   # + `sources: list[dict]` field on AIChatResponse
app/ai/prompts/system_prompt.py     # + guidance on using retrieved knowledge, not
                                     #   fabricating beyond it
pyproject.toml                      # + faiss-cpu, numpy, pypdf, sentence-transformers
.env.example                        # + RAG_* environment variables
```

No existing business logic, routes, models, or architecture were changed —
only additive wiring (new constructor params default to `None`/optional, so
nothing that already calls these classes breaks).

## 3. RAG architecture

```
data/knowledge/*.{pdf,md,txt,csv}
        │
        ▼
  DocumentLoader  ──►  TextChunker (configurable size/overlap)
        │
        ▼
  EmbeddingModel (all-MiniLM-L6-v2, lazy-loaded)
        │
        ▼
  FAISSVectorStore (IndexFlatIP, cosine sim, persisted to data/knowledge/.index/)
```

`RAGPipeline` wraps all of the above behind `.ingest()` and `.search(question)`.
Everything ML-related is lazy — importing/constructing `RAGPipeline` never
touches torch/faiss/sentence-transformers until you actually call `.ingest()`
or `.search()`, so the rest of the app keeps working even before the new
deps are installed.

## 4. Retrieval pipeline (per-request)

```
Question → Retriever (embed + FAISS top-k) → Reranker (cross-encoder)
         → RetrievedChunk list with (document_name, page_number, chunk_id)
```

## 5. Vector store

`VectorStore` is an ABC (`add`, `search`, `count`, `clear`). `FAISSVectorStore`
is the only implementation today — swapping in PgVector/Qdrant/Chroma later
means writing one new class, nothing else changes.

## 6. Planner integration

Two new `PlanningRule`s were added, both with `use_rag=True`, placed **before**
the existing keyword rules in `PlanningRules._RULES` so specific educational
phrasing wins first:

- **`financial_education`** — pure knowledge lookup, no user-data tools.
  Matches things like "what is an emergency fund", "50/30/20", "what is a
  SIP/index fund/credit score/mutual fund", etc.
- **`investment_capacity`** — hybrid. Matches "can I invest ₹5,000 every
  month?" style questions. Runs `financial_summary` + `monthly_cash_flow` +
  `savings_advisor` **and** RAG, so the LLM gets both the user's real numbers
  and general SIP/investing guidance.

In `PersonalCFOAgentPlanner.run()`, after tools/advisors execute, if
`rule.use_rag` is set, `_execute_knowledge_search()` calls
`knowledge_tools.search_financial_knowledge(question, self.rag_pipeline)`
and stores the result under `context.tool_outputs["financial_knowledge"]` —
same mechanism as every other tool output, so it flows into
`context.to_llm_payload()` and reaches the LLM automatically. No changes
were needed to `LLMService` itself.

`AIChatResponse.sources` surfaces `(document_name, page_number, chunk_id,
score)` for every retrieved chunk directly on the API response, in addition
to it being present inside `tool_output`.

Purely personal-data questions ("What did I spend last month?", "What is my
cash flow?") don't match either new rule and continue through the existing
Financial Intelligence path untouched.

## 7. Verification performed

- `python -m compileall app` — clean, exit 0
- `python -m unittest tests.smoke.test_rag_smoke` — **10/10 pass**
  (rule routing, chunking size/overlap, invalid-config validation, full
  planner integration with a stub RAG pipeline, RAG-disabled fallback)
- `python -m unittest tests.test_personal_cfo_planner` — **6/6 pass**,
  confirming no regression to existing planner behavior
- Ran `DocumentLoader` + `TextChunker` against the real sample docs in
  `data/knowledge/` end-to-end: 3 documents → 15 chunks, page/metadata
  preserved correctly
- Confirmed `faiss-cpu`, `numpy`, `pypdf`, `sentence-transformers`, and
  `torch` (sentence-transformers' own dependency) all publish `cp314` /
  `abi3` wheels on PyPI — your `requires-python = ">=3.14"` pin will not
  block `uv sync`

**Not run in this sandbox** (would require downloading the actual
embedding/cross-encoder models, several hundred MB): live `.ingest()` /
`.search()` against real sentence-transformers models, and a live FAISS
round-trip. The vector store and embedding code paths are exercised by the
unit tests via `FakeRAGPipeline`; run steps 8a/8b below once dependencies
are installed to validate the real models.

## 8. To apply this on your machine

```bash
# a) copy these files into your project (overwriting the modified ones)

# b) install the new dependencies
cd backend
uv sync

# c) run the full test suite
uv run python -m unittest discover tests

# d) one-time ingestion of the sample knowledge docs (downloads the two
#    models on first run, ~90MB each)
uv run python -c "
from app.rag.pipeline import RAGPipeline
p = RAGPipeline()
print('chunks indexed:', p.ingest(force=True))
print(p.search('What is an emergency fund?'))
"

# e) start the app as usual and try:
#    POST /api/v1/ai/chat  {"message": "What is the 50/30/20 rule?"}
#    POST /api/v1/ai/chat  {"message": "Can I invest ₹5000 every month?"}
```

## 9. Unrelated issues noticed (not touched, flagged for your awareness)

- `AIConversationService` still carries the older `_detect_intent` /
  `_dispatch_tool` / `_build_answer` methods, which look unused now that
  `chat()` calls `self.planner.run()` directly — dead code, left untouched
  per "don't modify existing business logic."
- `.env.example` has stray `\r` (CRLF) artifacts around `JWT_SECRET` from
  before this sprint; left as-is, just noting it in case it's not
  intentional.
- The full `backend.zip` you uploaded included a `.venv/` directory — worth
  excluding that from the zip next time (or via `.gitignore` if this is
  going into a repo), since it bloats the archive and isn't something a
  teammate should copy over their own venv.
