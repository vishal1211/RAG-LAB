from langchain_groq import ChatGroq
from ..settings import settings

llm = ChatGroq(model=settings.model_name, api_key=settings.groq_api_key, temperature=0)


def rewrite_query(
    query: str, history: list[dict] | None = None, summary: str = ""
) -> str:
    """
    Rewrites the query based on the conversation history.
    If there's no history, it returns the original query.
    """

    if not history and not summary:
        return query

    # Create a prompt for the LLM to rewrite the query
    conversation_history = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in history]
    )
    prompt = f"""
            Rewrite the current question into a standalone question.

            Use the conversation summary and recent conversation only to resolve context and references.

            Do not answer the question.
            Return only the rewritten question.
            Conversation summary:
            {summary}
            Recent conversation:
            {conversation_history}

            Current question:
            {query}
            """

    # Use the LLM to generate a rewritten query
    rewritten_query = llm.invoke(prompt).content.strip()

    return rewritten_query
