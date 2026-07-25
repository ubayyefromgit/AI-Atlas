# AI Atlas: Architecture & Design Decisions

## 1. Overview
AI Atlas is a scalable, AI-powered intelligence platform tailored for the Food & Beverage (F&B) sector. It combines a Grounded RAG (Retrieval-Augmented Generation) pipeline with an autonomous **AI Agent Extension Layer** to enable natural language discovery of AI companies, solutions, news, and market intelligence relevant to the industry.

This document details the architectural choices, the underlying data model, retrieval & agent design, news pipeline mechanics, update strategies, deployment architecture, trade-offs, and future improvements.

---

## 2. Data Model
The system relies on a hybrid persistence strategy, using a relational database (SQLite via SQLAlchemy) for structured metadata and a vector database (ChromaDB) for semantic embeddings.

### Relational Schema (SQLite)
The primary entities include:
- **Company**: Stores core entity information (name, website, location, summary, maturity, revenue, AI category).
- **Sector/Problem**: Categorization of business domains and specific pain points solved by companies (e.g., Quality Control, Supply Chain Optimization).
- **Discovery**: Maintains mapping and candidates of how companies fit into specific AI/F&B discovery themes.
- **News**: Stores relevant articles fetched from news providers, mapped to companies with relevance scores and summaries.
- **Notification**: Manages user notifications (e.g., when new relevant news is ingested).

### Vector Schema (ChromaDB)
- **KB Chunk**: Knowledge Base chunks are stored as vectors in ChromaDB. Each chunk represents segmented text from company descriptions, problems, and recent news. These vectors enable dense semantic search during retrieval.

---

## 3. Retrieval Design & Grounded RAG
The RAG pipeline is implemented in the `backend/services/ask_ai` module. It bridges user queries with factual, grounded context.

### Query Processing & Analysis
1. **Query Analyzer**: Evaluates user input using an LLM to extract keywords, intent, and filters (e.g., location, sector).
2. **Context Manager**: Uses the analyzed query to perform dense vector search on ChromaDB, retrieving the top `KB Chunk`s. 
3. **Structured Fallback**: If vector search yields low confidence, standard SQL text matching acts as a fallback to ensure relevant results.

### Response Generation
1. **Prompt Builder**: Synthesizes retrieved chunks into a system prompt instructing the LLM to generate answers strictly based on provided context.
2. **Citation Extractor**: Identifies source citations linked back to original companies or news articles.
3. **Response Formatter**: Formats final payload for frontend presentation.

---

## 4. AI Agent Extension Layer (`backend/services/agent`)

The application includes an **AI Agent Layer** following the Open-Closed Principle. Existing services act as tools orchestrated by the `AgentService`.

```
                  ┌─────────────────────────────────────────┐
                  │          User Query / Client            │
                  └────────────────────┬────────────────────┘
                                       │
                         ┌─────────────┴─────────────┐
                         ▼                           ▼
                 /api/v1/ask                 /api/v1/agent/chat
                (Grounded RAG)               (AI Agent Mode)
                         │                           │
                         │                           ▼
                         │                    ┌──────────────┐
                         │                    │ AgentService │
                         │                    └──────┬───────┘
                         │                           │
                         │             ┌─────────────┴─────────────┐
                         │             ▼                           ▼
                         │     ┌───────────────┐           ┌──────────────┐
                         │     │ ToolRegistry  │           │ AgentMemory  │
                         │     └───────┬───────┘           └──────────────┘
                         │             │
        ┌────────────────┼─────────────┼────────────────┬────────────────┐
        ▼                ▼             ▼                ▼                ▼
┌───────────────┐ ┌─────────────┐ ┌──────────┐ ┌────────────────┐ ┌──────────────┐
│ KnowledgeTool │ │  NewsTool   │ │Discovery │ │GeneralKnowledge│ │ Agent Jobs   │
│ (Grounded RAG)│ │(News Engine)│ │   Tool   │ │ Tool (Fallback)│ │ (Auto-Disc.) │
└───────────────┘ └─────────────┘ └──────────┘ └────────────────┘ └──────────────┘
```

### Planner Flow
The `AgentService` implements a structured execution flow:
```text
User Query ──► Intent Detection ──► Tool Selection ──► Tool Execution ──► Response Merge ──► Return Answer
```

### Tool Registry (`ToolRegistry`)
Exposes existing application core services as modular tools without duplicating business logic:
- **KnowledgeTool**: Wraps `KnowledgeBaseService` and `AskService` for grounded RAG query resolution over internal entities.
- **NewsTool**: Wraps `NewsService` for fetching, summarizing, and presenting recent F&B industry news.
- **DiscoveryTool**: Wraps `QuickDiscoveryService` for live market intelligence and company candidate search.
- **GeneralKnowledgeTool**: Wraps `LLMFactory` for general reasoning when questions fall outside project domain knowledge.

### General Knowledge Fallback Strategy
- When retrieval confidence is below `MIN_RETRIEVAL_SCORE` and context is missing:
  - Invokes `GeneralKnowledgeTool` using Gemini/Groq general reasoning.
  - Automatically appends mandatory disclaimer:
    > *"This answer is based on general knowledge and not the project knowledge base."*

### Agent Memory (`AgentMemory`)
- Maintains lightweight, non-vector in-memory conversation context keyed by `conversation_id`.
- Stores `last_queries`, `last_responses`, `tool_usage`, and turns to support multi-turn conversational follow-ups.

### Automatic Company Discovery & News Monitoring Jobs
- **Agent Discovery Job**: Evaluates discovery candidates. If confidence $\ge$ `AUTO_DISCOVERY_THRESHOLD` (default 0.90), it automatically creates the company and indexes it into the Knowledge Base without requiring manual admin approval. Candidates below 0.90 are retained as `PENDING_REVIEW`.
- **Agent News Monitor Job**: Fetches news, maps articles to companies, and automatically indexes new summaries into the Knowledge Base.

---

## 5. News Pipeline
The news ingestion pipeline (`backend/services/news`) keeps platform intelligence current:

1. **Providers**: Uses modular providers (`google_rss_provider`, `gnews_provider`).
2. **Ingestion & Deduplication**: Fetches matching articles; `deduplicator.py` filters identical or near-duplicate articles.
3. **Relevance Filtering**: `relevance_filter.py` applies zero-shot classification to score F&B sector relevance.
4. **Summarization**: `summarizer.py` generates concise summaries.
5. **Indexing**: `news_indexer.py` updates SQLite and pushes summaries into ChromaDB as KB chunks.

---

## 6. Deployment Architecture

### Dual Free-Tier Hosting Setup
- **Backend**: Hosted on **Render** (Free Tier Web Service running Python 3.11 / Uvicorn).
- **Frontend**: Hosted on **Vercel** (Free Tier CDN with SPA rewrites configured via `frontend/vercel.json`).

### RAM Optimization Strategy
Render's free tier imposes a strict **512 MB RAM limit**. To avoid Out-Of-Memory (OOM) process crashes:
- **Startup Auto-Seeding**: Checks SQLite database on boot. If empty, automatically populates 116 companies, 71 problems, 15 sectors, and 24 mappings from `data/atlas_dataset/` CSV files (~30MB RAM).
- **Lazy Vector Indexing**: Skips heavy PyTorch batch vector indexing on server startup, ensuring background memory remains below 150MB.

---

## 7. Trade-offs

### Relational SQLite vs. PostgreSQL
- *Decision*: SQLite was chosen for zero-configuration, rapid development, and single-file portability.
- *Trade-off*: Limited concurrency for heavy concurrent writes. Migration to PostgreSQL would be required for high-throughput scaling.

### Local ChromaDB vs. Managed Vector DB
- *Decision*: Local ChromaDB instance used for MVP to reduce infrastructure costs.
- *Trade-off*: Horizontal scaling across multi-node backend clusters requires a cloud vector database (e.g., Pinecone, Qdrant).

---

## 8. What We'd Improve with More Time

1. **Asynchronous Task Queue (Celery/Redis)**: Offload news fetching, LLM summarization, and vector indexing to background workers.
2. **Graph Database Integration**: Incorporate Neo4j for multi-hop graph queries across companies, sectors, and problem categories.
3. **Hybrid Vector Search**: Implement hybrid BM25 + dense vector search for improved retrieval precision.
