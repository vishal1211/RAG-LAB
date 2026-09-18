from .relevance_evaluator import is_document_relevant
from langchain_groq import ChatGroq
from .retriever import retrieve_documents
from ..settings import settings

llm = ChatGroq(model=settings.model_name, api_key=settings.groq_api_key, temperature=0)


def rewrite_for_retrieval(query: str) -> str:
    prompt = f"""
Rewrite the query to improve semantic document retrieval.

Make it specific and information-rich.
Do not answer the query.
Return only the rewritten query.

Query:
{query}
"""

    response = llm.invoke(prompt)

    return response.content.strip()


def evaluate_results(query: str, results):
    evaluated_results = []

    for document, distance in results:
        relevant = is_document_relevant(
            query=query, document_text=document.page_content
        )

        if relevant:
            evaluated_results.append((document, distance))

    return evaluated_results


def corrective_retrieve(query: str, strategy: str):
    search_text, results, _ = retrieve_documents(query, use_hyde=strategy == "hyde")
    evaluated_results = evaluate_results(query, results)

    if evaluated_results:
        return {
            "results": evaluated_results,
            "search_text": search_text,
            "corrected_query": None,
            "corrected": False,
            "is_relevant": True,
        }

    corrected_query = rewrite_for_retrieval(query)

    retry_search_text, retry_results, _ = retrieve_documents(
        corrected_query, use_hyde=False
    )
    evaluated_results = evaluate_results(query, retry_results)

    return {
        "results": evaluated_results,
        "search_text": retry_search_text,
        "corrected_query": corrected_query,
        "corrected": True,
        "is_relevant": bool(evaluated_results),
    }
