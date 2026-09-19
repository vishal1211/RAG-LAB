# RAG Lab — Backend

Python + FastAPI backend for **RAG Lab**, a document-grounded question-answering application. Users upload PDFs, and the system extracts and chunks text, embeds it, retrieves relevant context, and generates answers with an LLM.

> **API documentation:** https://rag-lab-production.up.railway.app/docs  
> **Health endpoint:** https://rag-lab-production.up.railway.app/health  
> **Source code:**  https://github.com/vishal1211/RAG-LAB/tree/main

## Architecture

```text
PDF upload
   → text extraction / document validation
   → chunking
   → Hugging Face text embeddings
   → Chroma vector store

Question + session ID
   → load conversation context
   → rewrite question when needed
   → retrieve document chunks (normal / HyDE strategy)
   → assess relevance / corrective retrieval when needed
   → generate answer with Groq-hosted LLM
   → verify grounding and save conversation state
   → answer + supporting context to React
```

Implementation details and which optional retrieval branch is taken should be confirmed against the current source code and runtime configuration.

## Features implemented during the project

- PDF upload and text extraction.
- Text splitting with configurable chunk size and overlap.
- Sentence Transformer embeddings and Chroma vector search.
- Duplicate-document handling.
- Session-based conversation history in SQLite, plus conversation summarization.
- Query rewriting for follow-up questions.
- HyDE (hypothetical document embeddings), retrieval strategy selection, and corrective retrieval.
- LLM-based relevance evaluation and answer verification.
- Agent-style controller with bounded retrieval/correction flow.
- FastAPI routes, healthcheck, Docker packaging, and Railway deployment.

## Tech stack

- Python 3.12, FastAPI, Pydantic Settings
- `uv` package manager
- LangChain and Chroma
- `sentence-transformers/all-MiniLM-L6-v2` embedding model (384 dimensions)
- Groq-hosted generation model (check `settings.py` for the selected model)
- SQLite conversation storage
- Docker and Railway

## Relevant project layout

```text
RAG-LAB/
└── backend/
    ├── Dockerfile
    ├── .dockerignore
    ├── pyproject.toml
    ├── uv.lock
    ├── README.md
    └── src/backend/
        ├── __init__.py           # FastAPI app served as backend:app
        ├── settings.py
        ├── upload.py             # upload router
        ├── api/
        ├── services/pdf_service.py
        └── rag/
            ├── chunking.py
            ├── vector_store.py
            ├── retriever.py
            ├── generator.py
            ├── memory.py
            ├── memory_summary.py
            ├── query_rewriter.py
            ├── hyde.py
            ├── retrieval_strategy.py
            ├── relevance_evaluator.py
            ├── corrective_retrieval.py
            ├── answer_verifier.py
            ├── agent_controller.py
            └── agentic_rag.py
```

## Local setup

Prerequisites: Python 3.12, `uv`, and credentials for the APIs enabled in your application.

```bash
cd backend
uv sync --frozen
```

Create a local `backend/.env` file with the **names actually declared in your `settings.py`**. The Railway deployment uses these names:

```env
GROQ_API_KEY=your_groq_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
VECTOR_STORE_PATH=data/vector_store
MEMORY_DB_PATH=data/conversation_memory.db
```

The Hugging Face key may not be necessary for a locally downloadable public embedding model, but the current settings validator may require it; check `settings.py`. If your actual SQLite setting has a different name, use that instead of `MEMORY_DB_PATH`.

Start the API from `backend/`:

```bash
uv run uvicorn backend:app --reload --host 127.0.0.1 --port 8000
```

If the src-layout package is not installed in the active environment, use `uv run uvicorn backend:app --app-dir src --reload --host 127.0.0.1 --port 8000`.

Open http://localhost:8000/docs and http://localhost:8000/health.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/upload/file` | Ingest a PDF |
| POST | `/api/v1/upload/search` | Retrieve context and answer a question |
| GET | `/health` | Healthcheck |
| GET | `/docs` | OpenAPI / Swagger UI |

The specific upload field name, search request model, source metadata, and response schema are defined by the current FastAPI source and available in `/docs`.

## Run with Docker

From `backend/`, build the image:

```bash
docker build -t rag-lab-backend .
```

Run on port 8000 using your private `.env` file and persist local data:

```bash
docker run --rm -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  rag-lab-backend
```

For Docker, use container paths for the Chroma and SQLite environment variables if needed:

```env
VECTOR_STORE_PATH=/app/data/vector_store
MEMORY_DB_PATH=/app/data/conversation_memory.db
```

Make sure your Dockerfile's Uvicorn entrypoint matches the app module (`backend:app`) and listens on `0.0.0.0:8000`. Confirm configuration with `/health` after starting.

## Deploy to Railway

- Deploy the `backend/Dockerfile` from the monorepo.
- Set production secrets in Railway **Variables**, never in Git or frontend code.
- Set `PORT=8000` if Uvicorn listens on 8000.
- Configure the public domain's **target port** to `8000` as well. This fixed the original public-routing issue during deployment.
- Configure a healthcheck for `/health`.
- Attach a persistent Railway volume at `/app/data` and configure Chroma / SQLite paths under that directory.
- Allow the exact Vercel origin in FastAPI CORS middleware.

Example production environment variables:

```env
PORT=8000
GROQ_API_KEY=***
HUGGINGFACE_API_KEY=***
VECTOR_STORE_PATH=/app/data/vector_store
MEMORY_DB_PATH=/app/data/conversation_memory.db
```

Railway resource quotas and free-trial credits may limit how long the service stays available. Preserve backups of any important uploaded data and vectors.

## RAG engineering considerations

### Chunking and retrieval

Chunk size and overlap trade off context completeness, embedding cost, and retrieval precision. Test with actual project PDFs instead of relying on one universal setting. Understand whether Chroma returns a **distance** (lower can be better) or similarity value before interpreting or filtering scores.

### Conversation-aware retrieval

For follow-up questions, use conversation context to formulate a stand-alone retrieval query while keeping the original user intent. Summaries and stored messages can help limit context size.

### Corrective RAG and grounding

If retrieved passages are weak, adjust retrieval rather than forcing the generator to answer without evidence. An answer verifier is a useful guardrail, but an LLM-based verifier is not a guarantee of factual correctness.

### Evaluation

Test retrieval relevance, answer support, missing-document behavior, unrelated questions, PDF extraction errors, duplicate uploads, session isolation, and deployment persistence. Use a small question/answer/reference set for regression checks.

## Security and production hardening

This is a learning and portfolio implementation, **not a claim of production readiness**. Before allowing unrestricted public use, consider:

- File size/type validation and limits on document processing.
- Authentication or quotas, because public PDF uploads and LLM calls consume resources.
- Protecting API keys and session data; avoiding logging sensitive document text.
- User/document isolation and deletion policies if multiple people upload PDFs.
- Timeouts and error handling for external model APIs.
- Backups, monitoring, and cost alerts.

## Future improvements

- Automated RAG evaluation dataset and regression pipeline.
- Improved source citations and per-document filtering.
- Background ingestion for larger PDFs.
- Authentication, per-user document isolation, and rate limiting.
- Better observability for retrieval decisions, latency, and token usage.

## License

Add your chosen license and a `LICENSE` file before publishing if you want to specify reuse permissions.
