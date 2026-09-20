# AFRAB CFO Roadmap

AFRAB CFO is a personal finance platform built with FastAPI, PostgreSQL,
SQLAlchemy, Alembic and an AI financial-assistance layer.

The AI architecture follows this principle:

> Interpret the user's request with AI,
> validate execution with deterministic application logic,
> retrieve trusted data through authorized tools,
> perform financial calculations deterministically,
> and use the LLM to explain the verified result.

---

# 🏗️ Overall Architecture

## Current Architecture

User
  ↓
FastAPI
  ↓
AI Conversation Service
  ↓
Memory
  ↓
Planner
  ↓
Tools / Advisors / RAG
  ↓
Existing Services
  ↓
Repositories
  ↓
PostgreSQL
  ↓
Structured Financial Context
  ↓
LLM
  ↓
Natural Language Response


## Target AI Architecture

User
  ↓
AI Interpreter
  ↓
Structured Request
  ↓
Deterministic Planner
  ↓
Plan Validation
  ↓
Tools / Advisors / RAG / External APIs
  ↓
Verified Context
  ↓
Deterministic Financial Reasoning
  ↓
LLM
  ↓
User


## Core Architecture Principles

- Financial data comes from the application/database, not the LLM.
- Business logic belongs in services.
- Persistence belongs in repositories.
- AI tools reuse existing services.
- RAG provides general financial knowledge.
- User-specific financial information comes through authorized tools/services.
- Financial calculations should be deterministic.
- The LLM should primarily interpret and explain rather than invent financial facts.
- Complexity should only be introduced when the product actually requires it.


---

# ✅ Sprint 1 — Backend Foundation

## Authentication & Core Domain

- [x] Authentication
- [x] Users
- [x] Accounts
- [x] Categories
- [x] Transactions
- [x] Dashboard
- [x] Opening Balance Refactor

## Architecture

- [x] FastAPI application structure
- [x] PostgreSQL integration
- [x] SQLAlchemy ORM
- [x] Alembic migrations
- [x] Repository layer
- [x] Service layer
- [x] API/router layer
- [x] User-scoped data access


---

# ✅ Sprint 2 — Budget Module

- [x] Budget Model
- [x] Alembic Migration
- [x] Schema
- [x] Repository
- [x] Service
- [x] API
- [x] Swagger Testing
- [x] Budget utilization logic
- [x] Budget API tests


---

# ✅ Sprint 3 — Goals

- [x] Goal Model
- [x] Alembic Migration
- [x] Schema
- [x] Repository
- [x] Service
- [x] API
- [x] Swagger Testing
- [x] Goal progress functionality
- [x] Goal API tests


---

# ✅ Sprint 4 — Transfers

- [x] Transfer Model
- [x] Alembic Migration
- [x] Transfer Schema
- [x] Transfer Repository
- [x] Transfer Service
- [x] Transfer API
- [x] Source Account
- [x] Destination Account
- [x] Transfer Date
- [x] Transfer Balance Handling
- [x] Transfer Service Tests
- [x] Transfer API Tests

## Transfer Accounting Rule

Current account balance is calculated as:

Opening Balance
+ Income
- Expenses
- Transfers Out
+ Transfers In

Transfers are treated as transfers between accounts,
not as income or expenses.


---

# ✅ Sprint 5 — Recurring Transactions

- [x] Recurring Transaction Model
- [x] Schema
- [x] Repository
- [x] Service
- [x] API
- [x] API Tests


---

# ⏳ Sprint 6 — Reports

## Planned

- [ ] Financial Reports
- [ ] Income vs Expense
- [ ] Category Spending
- [ ] Savings Analysis
- [ ] Financial Trends
- [ ] Monthly Financial Summary
- [ ] Report API
- [ ] Report Tests

## Future Financial Intelligence

- [ ] Spending trends
- [ ] Savings trends
- [ ] Cash-flow trends
- [ ] Net-worth reporting
- [ ] Debt reporting
- [ ] Financial health metrics


---

# 🚧 Sprint 7 — AI CFO Foundation

## AI Chat

- [x] AI Chat API
- [x] AI Conversation Service
- [x] AI System Prompt
- [x] Personal CFO Agent Foundation

## Planner

- [x] Intent-based planning
- [x] Deterministic Planner
- [x] Planning Rules
- [x] Execution Context

## AI Tools

- [x] Financial Tools
- [x] Account Tools
- [x] Transaction Tools
- [x] Budget Tools
- [x] Goal Tools
- [x] Category Tools
- [x] Dashboard Tools
- [x] Recurring Transaction Tools
- [x] Advisor Tools
- [x] Knowledge Tools

## Advisors

- [x] Spending Advisor
- [x] Budget Advisor
- [x] Goal Advisor
- [x] Savings Advisor
- [x] Financial Health Advisor

## Current AI Design

The AI layer does not directly query the database for every request.

Instead:

AI
 ↓
Planner
 ↓
Tool
 ↓
Existing Service
 ↓
Repository
 ↓
Database

This keeps the AI layer separated from core business logic.


---

# 🚧 Sprint 8 — AI Memory

## Memory Foundation

- [x] Conversation Memory Model
- [x] Memory Repository
- [x] Memory Service
- [x] Memory API
- [x] User-scoped memory
- [x] Short-Term Memory
- [x] Preference Memory Foundation
- [x] Financial Context Memory Foundation
- [x] Context Builder
- [x] Memory Manager
- [x] Conversation Summarizer
- [x] Memory Cleanup
- [x] Memory Tests

## Current Memory Direction

The current foundation supports:

- Conversation history
- Short-term context
- Preference storage foundation
- Financial-context storage foundation
- Context construction
- Conversation summarization/compaction

## Future Memory Improvements

- [ ] Automatic Preference Extraction
- [ ] Stable Fact Extraction
- [ ] Memory Relevance Filtering
- [ ] Memory Importance Scoring
- [ ] Memory Conflict Resolution
- [ ] Memory Expiration
- [ ] Session Management
- [ ] Semantic Memory Retrieval
- [ ] Better Financial Context Retrieval
- [ ] Memory Evaluation Tests


---

# 🚧 Sprint 9 — Financial Knowledge / RAG

## RAG Foundation

- [x] Document Loader
- [x] Document Chunking
- [x] Embeddings
- [x] FAISS Vector Store
- [x] Retriever
- [x] Cross-Encoder Reranker
- [x] Ingestion Pipeline
- [x] RAG Pipeline
- [x] Knowledge Tools

## Knowledge Base

- [x] Budgeting Basics
- [x] Investing Basics
- [x] Credit Basics

## Current RAG Flow

Documents
 ↓
Loader
 ↓
Chunking
 ↓
Embeddings
 ↓
Vector Store
 ↓
Retriever
 ↓
Reranker
 ↓
Relevant Knowledge
 ↓
AI Knowledge Tool

## Future

- [ ] Expand Financial Knowledge Base
- [ ] Retrieval Evaluation
- [ ] RAG Testing
- [ ] Source Metadata
- [ ] Source/Citation Handling
- [ ] Retrieval Quality Evaluation
- [ ] Knowledge Freshness Strategy


---

# ✅ Sprint 10 — Backend & AI Testing Foundation

## Backend Tests

- [x] Authentication Tests
- [x] Account Tests
- [x] Transaction Tests
- [x] Category Tests
- [x] Budget Tests
- [x] Goal Tests
- [x] Recurring Transaction Tests
- [x] Dashboard Tests
- [x] Transfer Tests

## AI Tests

- [x] Memory Tests
- [x] AI Chat Tests
- [x] Planner Tests
- [x] RAG Smoke Tests

## Current Status

**172 tests passing**

The test suite provides coverage across the core backend,
financial modules, AI foundation, memory and planner components.


---

# 🚧 Sprint 11 — AI Interpreter & Structured Planning

## Objective

Evolve the current deterministic intent/planning foundation into
a structured AI interpretation layer.

## Current

User
 ↓
Intent-based Planning
 ↓
Deterministic Planner
 ↓
Tools


## Target

User
 ↓
AI Interpreter
 ↓
Structured Request
 ↓
Deterministic Planner
 ↓
Validation
 ↓
Tools / Advisors / RAG
 ↓
Verified Context


## AI Interpreter

- [ ] Define structured AI request schema
- [ ] Interpret natural-language financial requests
- [ ] Extract intent
- [ ] Extract required parameters
- [ ] Identify missing parameters
- [ ] Detect ambiguous requests
- [ ] Map interpreted requests to existing planner intents

## Structured Planning

- [ ] Define structured execution-plan schema
- [ ] Support single-step plans
- [ ] Support multi-step plans
- [ ] Define required tools
- [ ] Define execution context

## Plan Validation

- [ ] Validate intent
- [ ] Validate parameters
- [ ] Validate tool availability
- [ ] Validate user authorization
- [ ] Reject invalid plans
- [ ] Handle planner failures safely

## Integration

- [ ] Integrate interpreter with AIConversationService
- [ ] Integrate with existing deterministic planner
- [ ] Reuse existing AI tools
- [ ] Reuse existing advisors
- [ ] Reuse memory context
- [ ] Reuse RAG

## Testing

- [ ] Interpreter tests
- [ ] Structured plan tests
- [ ] Validation tests
- [ ] Ambiguous request tests
- [ ] Invalid plan tests
- [ ] End-to-end planning tests


---

# ⏳ Sprint 12 — Financial Reasoning Engine

## Objective

Separate deterministic financial calculations and reasoning
from the LLM.

## Financial Calculations

- [ ] Net Worth
- [ ] Savings Rate
- [ ] Monthly Burn Rate
- [ ] Expense Trends
- [ ] Budget Variance
- [ ] Goal Projection
- [ ] Debt Analysis
- [ ] EMI Calculations
- [ ] Interest Calculations
- [ ] Emergency Fund Analysis
- [ ] Cash-Flow Analysis

## Financial Reasoning

- [ ] Spending pattern analysis
- [ ] Budget deviation analysis
- [ ] Savings analysis
- [ ] Goal feasibility analysis
- [ ] Debt reasoning
- [ ] Financial health calculations
- [ ] Scenario analysis

## Architecture

The financial reasoning layer should calculate verified results:

Financial Data
 ↓
Deterministic Calculation
 ↓
Financial Result
 ↓
LLM
 ↓
Explanation

The LLM should not be responsible for performing
authoritative financial calculations.


---

# ⏳ Sprint 13 — Live External Financial Information

## Objective

Allow AFRAB CFO to retrieve information that changes over time.

## External APIs

- [ ] External API integration framework
- [ ] Currency Exchange API
- [ ] Live FX Tool
- [ ] Market Data Integration
- [ ] External Financial Information Tool

## Example

User:

"Convert ₹50,000 to USD today."

 ↓

AI Interpreter

 ↓

Currency Tool

 ↓

Live FX API

 ↓

Current Exchange Rate

 ↓

Deterministic Calculation

 ↓

LLM Explanation

## Reliability

- [ ] API timeout handling
- [ ] API failure handling
- [ ] Rate limiting
- [ ] Caching
- [ ] Source timestamp
- [ ] External-data validation
- [ ] Observability


---

# 🚧 Sprint 14 — AI CFO End-to-End Orchestration

## Objective

Connect all existing AI capabilities into a reliable
end-to-end Personal CFO workflow.

## Target

User
 ↓
AI Interpreter
 ↓
Structured Request
 ↓
Planner
 ↓
Validation
 ↓
Tools / Advisors / RAG / External APIs
 ↓
Verified Context
 ↓
Financial Reasoning
 ↓
LLM
 ↓
User

## Planned

- [ ] End-to-end orchestration
- [ ] Multi-step user requests
- [ ] Tool execution pipeline
- [ ] Context aggregation
- [ ] Financial reasoning integration
- [ ] RAG integration
- [ ] Memory integration
- [ ] External API integration
- [ ] LLM response generation
- [ ] Error recovery
- [ ] Execution tracing
- [ ] End-to-end tests


---

# ⏳ Sprint 15 — Production AI Engineering

## Observability

- [ ] Structured Logging
- [ ] AI Execution Tracing
- [ ] Tool Execution Tracing
- [ ] LLM Latency Tracking
- [ ] Token Usage Tracking
- [ ] Error Tracking

## Reliability

- [ ] Timeout Handling
- [ ] Retry Strategy
- [ ] Graceful AI Failure
- [ ] External API Failure Handling
- [ ] Fallback Handling

## Performance

- [ ] Database Query Optimization
- [ ] Database Index Review
- [ ] RAG Performance Optimization
- [ ] LLM Latency Optimization
- [ ] Caching Strategy

## Security

- [ ] Authorization Review
- [ ] User Data Isolation Review
- [ ] AI Tool Authorization
- [ ] Input Validation Review
- [ ] Prompt Injection Protection
- [ ] Sensitive Data Handling
- [ ] Secret Management

## Deployment

- [ ] Production Configuration
- [ ] CI/CD
- [ ] Environment Management
- [ ] Production Database Migration Strategy
- [ ] Monitoring
- [ ] Backup Strategy


---

# ⏳ Sprint 16 — Advanced Personalization

## Memory

- [ ] Long-term user profile
- [ ] Financial preferences
- [ ] Personalized financial context
- [ ] Relevance-based memory retrieval

## Personalization

- [ ] Personalized spending insights
- [ ] Personalized budget suggestions
- [ ] Personalized savings suggestions
- [ ] Personalized goal suggestions
- [ ] Personalized financial explanations

## Context

- [ ] User financial profile
- [ ] Historical financial patterns
- [ ] Financial behavior context
- [ ] Personalized AI responses


---

# ⏳ Sprint 17 — Advanced AI Capabilities

## Potential Future Capabilities

- [ ] Complex multi-step financial questions
- [ ] Financial scenario simulation
- [ ] What-if analysis
- [ ] Goal optimization
- [ ] Debt payoff scenarios
- [ ] Savings scenarios
- [ ] Budget optimization
- [ ] Financial planning workflows

## Agent Architecture

A multi-agent architecture is **not currently required**.

Potential future architecture:

User
 ↓
CFO Orchestrator
 ├── Spending Agent
 ├── Budget Agent
 ├── Goal Agent
 ├── Savings Agent
 └── Financial Health Agent

This should only be introduced if the application reaches
a complexity level where specialized agents provide a real
engineering or product benefit.


---

# 🧪 Overall Testing Roadmap

## Completed

- [x] Authentication tests
- [x] Account tests
- [x] Transaction tests
- [x] Category tests
- [x] Budget tests
- [x] Goal tests
- [x] Recurring transaction tests
- [x] Dashboard tests
- [x] Transfer tests
- [x] Memory tests
- [x] AI Chat tests
- [x] Planner tests
- [x] RAG smoke tests

## Current

**172 tests passing**

## Future

- [ ] AI Interpreter tests
- [ ] Structured plan tests
- [ ] Plan validation tests
- [ ] Financial reasoning tests
- [ ] RAG evaluation tests
- [ ] Advisor evaluation tests
- [ ] Tool execution tests
- [ ] External API tests
- [ ] End-to-end AI tests
- [ ] Security tests
- [ ] Performance tests


---

# 🧠 AFRAB CFO Engineering Principles

## 1. Database is the source of truth

User financial data comes from:

PostgreSQL
 ↓
Repositories
 ↓
Services
 ↓
AI Tools

The LLM does not become the source of truth.

---

## 2. Business logic belongs in services

Router
 ↓
Service
 ↓
Repository
 ↓
Database

AI tools should reuse these services rather than duplicate
business logic.

---

## 3. AI Tools provide structured facts

Example:

get_budget_utilization()

returns structured financial data.

The tool retrieves facts.

---

## 4. Advisors interpret structured facts

Example:

Budget Tool
 ↓
Budget Advisor
 ↓
Financial interpretation

Tools retrieve information.

Advisors provide deterministic interpretation/heuristics.

---

## 5. RAG provides general financial knowledge

General financial knowledge
 ↓
RAG

User-specific financial information
 ↓
Authorized tools/services

These two sources should remain conceptually separate.

---

## 6. Financial calculations should be deterministic

LLM:
- Understands
- Interprets
- Explains

Application:
- Retrieves
- Calculates
- Validates
- Authorizes

---

## 7. Complexity should be earned

Do not introduce:

- Multi-agent systems
- Complex orchestration frameworks
- unnecessary RAG
- unnecessary autonomous agents

unless a real requirement justifies them.

---

# 🎯 Current AFRAB CFO Position

AFRAB CFO has moved beyond a basic CRUD backend.

## Backend Foundation

Authentication
Accounts
Transactions
Categories
Budgets
Goals
Transfers
Recurring Transactions
Dashboard

↓

## AI Foundation

AI Chat
Planner
AI Tools
Advisors
Memory
RAG
Personal CFO Agent Foundation
LLM Integration

↓

## Testing Foundation

172 tests passing

↓

## Next Architectural Evolution

AI Interpreter
 ↓
Structured Request
 ↓
Deterministic Planner
 ↓
Validation
 ↓
Tools / Advisors / RAG
 ↓
Verified Context
 ↓
Financial Reasoning
 ↓
LLM
 ↓
User


# 🚦 Immediate Development Priority

The next major focus should be:

1. Stabilize the existing architecture
2. Review the current Planner
3. Review AIConversationService
4. Review Memory integration
5. Review AI Tools
6. Implement the structured AI Interpreter
7. Add deterministic plan validation
8. Build financial reasoning separately
9. Add live external information only where required
10. Build complete end-to-end AI tests

The goal is not to keep adding features randomly.

The goal is to evolve AFRAB CFO from an AI-enabled backend into a
reliable Personal CFO system.