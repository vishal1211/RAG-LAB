from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import hashlib

from .services.pdf_service import extract_pdf_pages
from .rag.chunking import create_documents
from .rag.vector_store import vector_store

from .rag.memory import (
    get_history,
    add_message,
    get_summary,
    compact_memory,
)

from .rag.query_rewriter import rewrite_query
from .rag.retrieval_strategy import choose_retrieval_strategy
from .rag.agentic_rag import run_agentic_rag
from .settings import settings
from .tests.rag_evaluation_cases import evaluation_cases
from .api.models import (SearchResponse, UploadResponse)
upload_router = APIRouter(prefix="/upload", tags=["Upload"])


class SearchRequest(BaseModel):
    query: str
    session_id: str


@upload_router.post("/file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDF files are allowed."
        )

    file_bytes = await file.read()

    file_hash = hashlib.sha256(file_bytes).hexdigest()

    existing = vector_store.get(where={"file_hash": file_hash})

    if existing["ids"]:
        return {
            "message": "File already exists in the vector store.",
            "filename": file.filename,
            "stored": False,
            "duplicate": True,
            "file_hash": file_hash,
        }

    pages = extract_pdf_pages(file_bytes)

    documents = create_documents(pages, file_hash, file.filename)

    vector_store.add_documents(documents)

    return {
        "message": "File uploaded successfully.",
        "filename": file.filename,
        "stored": True,
        "duplicate": False,
        "file_hash": file_hash,
        "chunks_stored": len(documents),
    }


@upload_router.post("/search", response_model=SearchResponse)
def search_vectors(request: SearchRequest):

    # 1. Get long-term summary
    summary = get_summary(request.session_id)

    # 2. Get recent conversation history
    history = get_history(request.session_id, settings.memory_history_limit)

    # 3. Convert follow-up question
    # into standalone retrieval query
    retrieval_query = rewrite_query(
        query=request.query, history=history, summary=summary
    )

    # 4. Adaptive RAG decides normal / HyDE
    strategy = choose_retrieval_strategy(retrieval_query)

    # 5. Agentic RAG controls:
    # retrieve
    # correct
    # generate
    # verify
    # finish
    agent_result = run_agentic_rag(
        query=request.query,
        retrieval_query=retrieval_query,
        strategy=strategy,
        history=history,
        summary=summary,
    )

    answer = agent_result["answer"]
    relevant_results = agent_result["results"]

    # 6. Save conversation
    add_message(request.session_id, "user", request.query)

    add_message(request.session_id, "assistant", answer)

    # 7. Compact old memory
    compact_memory(request.session_id, keep_recent=settings.memory_history_limit)
    # test_rag_evaluation_cases()
    # 8. Return final response
    return {
        "original_query": request.query,
        "retrieval_query": retrieval_query,
        "strategy": strategy,
        "search_text": agent_result["search_text"],
        "answer": answer,
        "is_supported": agent_result["answer_supported"],
        "agent_trace": agent_result["trace"],
        "sources": [
            {
                "filename": document.metadata.get("filename"),
                "page": document.metadata.get("page"),
                "content": document.page_content,
                "distance": distance,
            }
            for document, distance in relevant_results
        ],
    }
