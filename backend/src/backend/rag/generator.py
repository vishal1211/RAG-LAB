from langchain_groq import ChatGroq
from ..settings import settings
from ..api.exceptions import GenerationError

llm = ChatGroq(
    model=settings.model_name, groq_api_key=settings.groq_api_key, temperature=0
)


def generate_answer(
    query: str, retrieved_results, history: list[dict] | None = None, summary: str = ""
) -> str:
    try:
        context = " ".join([doc.page_content for doc, score in retrieved_results])
        history_text = (
            "\n".join(f"{message['role']}: {message['content']}" for message in history)
            if history
            else ""
        )
        prompt = f"""
                        Answer the question using only the retrieved document context.

                        Use the conversation summary and recent conversation
                        only to understand references and conversational context.

                        Conversation summary:
                        {summary}

                        Recent conversation:
                        {history_text}

                        Retrieved document context:
                        {context}

                        Current question:
                        {query}

                        If the answer is not available in the retrieved document context, say:
                        "I don't know based on the provided document."
                        """
        response = llm.invoke(prompt)
        return response.content

    except Exception as exc:
        raise GenerationError("Failed to generate an answer.") from exc
