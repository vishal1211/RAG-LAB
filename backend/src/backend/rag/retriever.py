from .vector_store import vector_store
from ..settings import settings
from .hyde import generate_hypothetical_document
from ..api.exceptions import RetrievalError


def retrieve_documents(query: str, use_hyde: bool = False):

    try:
        search_text = query
        if use_hyde:
            search_text = generate_hypothetical_document(query)

        # Perform a similarity search in the vector store
        results = vector_store.similarity_search_with_score(
            search_text, k=settings.retrieval_k
        )

        # Filter results based on a distance threshold (e.g., 1.0)
        relevant_results = [
            (doc, distance)
            for doc, distance in results
            if distance <= settings.retrieval_distance_threshold
        ]
        is_relevant = len(relevant_results) > 0

        return search_text, relevant_results, is_relevant
    except Exception as exc:
        raise RetrievalError("Failed to retrieve relevant documents.") from exc
