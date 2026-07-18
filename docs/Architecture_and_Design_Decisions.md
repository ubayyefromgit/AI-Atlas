# AI Atlas: Architecture & Design Decisions

## 1. Overview
AI Atlas is a scalable, AI-powered intelligence platform tailored for the Food & Beverage (F&B) sector. It leverages a Grounded RAG (Retrieval-Augmented Generation) pipeline to enable natural language discovery of AI companies, solutions, and news relevant to the industry.

This document details the architectural choices, the underlying data model, retrieval design, news pipeline mechanics, update strategies, architectural trade-offs, and future improvements.

---

## 2. Data Model
The system relies on a hybrid persistence strategy, using a relational database (SQLite via SQLAlchemy) for structured metadata and a vector database (ChromaDB) for semantic embeddings.

### Relational Schema (SQLite)
The primary entities include:
- **Company**: Stores core entity information (name, website, location, summary).
- **Sector/Problem**: Categorization of the business domains and the specific pain points a company solves (e.g., Quality Control, Supply Chain Optimization).
- **Discovery**: Maintains mapping of how companies fit into specific AI/F&B discovery themes.
- **News**: Stores relevant articles fetched from news providers, mapped to companies with relevance scores and summaries.
- **Notification**: Manages user notifications (e.g., when new relevant news is ingested).

### Vector Schema (ChromaDB)
- **KB Chunk**: Knowledge Base chunks are stored as vectors in ChromaDB. Each chunk represents segmented text from company descriptions, problems, and recent news. These vectors enable dense semantic search during the retrieval phase.

---

## 3. Retrieval Design (Grounded RAG)
The RAG pipeline is implemented in the `backend/services/ask_ai` module. It bridges user queries with factual, grounded context.

### Query Processing & Analysis
1. **Query Analyzer**: Evaluates user input using an LLM to extract keywords, intent, and filters (e.g., location, sector).
2. **Context Manager**: Uses the analyzed query to perform a dense vector search on ChromaDB. It retrieves the most relevant `KB Chunk`s. 
3. **Structured Fallback**: If vector search yields low confidence, standard SQL text matching and filtering act as a fallback to ensure relevant results.

### Response Generation
1. **Prompt Builder**: Synthesizes the retrieved chunks into a robust system prompt, instructing the LLM to generate answers strictly based on the provided context.
2. **Citation Extractor**: The generated response is parsed to identify source citations, which are linked back to the original companies or news articles.
3. **Response Formatter**: Formats the final payload for the frontend, ensuring a clean, rich UI presentation.

---

## 4. News Pipeline
The news ingestion pipeline (`backend/services/news`) is designed to keep the platform's intelligence up-to-date.

1. **Providers**: Uses modular providers like `google_rss_provider` and `gnews_provider`.
2. **Ingestion & Deduplication**: Fetches articles matching company names and keywords. The `deduplicator.py` ensures identical or highly similar articles are ignored.
3. **Relevance Filtering**: `relevance_filter.py` applies an LLM-based zero-shot classification to score the article's relevance specifically to the F&B sector and the target company. Low-relevance articles are discarded.
4. **Summarization**: `summarizer.py` generates a concise summary of the article.
5. **Indexing**: `news_indexer.py` updates the SQLite database and pushes the new summaries into ChromaDB as new KB chunks.

---

## 5. Update Strategy
The platform ensures continuous data freshness without manual intervention.

- **Background Scheduler**: A background process (`backend/scheduler.py`) periodically triggers the news pipeline.
- **Differential Updates**: Instead of rebuilding the entire vector index, the system uses an append-only/upsert strategy for ChromaDB. Only new companies and newly validated news articles are indexed.
- **Notifications**: Users are alerted via the `Notification` model when high-relevance news alters the landscape for a company they follow.

---

## 6. Trade-offs

### SQLite vs. PostgreSQL
- *Decision*: SQLite was chosen for ease of deployment, zero-configuration setup, and local development speed.
- *Trade-off*: SQLite lacks native concurrency for heavy write workloads and advanced features (like JSONB). A migration to PostgreSQL would be necessary for high-throughput production environments.

### Local ChromaDB vs. Managed Vector DB
- *Decision*: Local ChromaDB instances are used for the MVP to reduce infrastructure costs and complexity.
- *Trade-off*: Scaling a local ChromaDB across multiple backend instances is challenging. A managed solution (e.g., Pinecone, Weaviate) would be required for horizontal scaling.

### On-the-fly LLM Relevance Filtering
- *Decision*: Using the LLM to score news relevance ensures high quality and contextual accuracy.
- *Trade-off*: It introduces latency and increases API costs during the ingestion phase. 

---

## 7. What We'd Improve with More Time

1. **Asynchronous Task Queue (Celery/Redis)**
   - *Improvement*: Offload the news fetching, LLM summarization, and vector indexing to a distributed task queue rather than a simple background scheduler loop. This would prevent blocking and allow horizontal scaling of workers.

2. **Graph Database Integration**
   - *Improvement*: Transition the relational mappings of Companies, Problems, and Technologies into a Graph Database (like Neo4j) to enable complex multi-hop queries (e.g., "Find companies solving supply chain issues using computer vision in Germany").

3. **Advanced RAG Strategies**
   - *Improvement*: Implement hybrid search (BM25 sparse + dense vectors), parent-child document retrieval, and query expansion to improve recall on complex user queries.

4. **Production-Ready Persistence**
   - *Improvement*: Migrate to PostgreSQL and a managed vector database to support clustering and high availability. Add Alembic for robust schema migrations.
