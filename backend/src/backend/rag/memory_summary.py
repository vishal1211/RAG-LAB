from langchain_groq import ChatGroq

from ..settings import settings

llm = ChatGroq(model=settings.model_name, api_key=settings.groq_api_key, temperature=0)


def summarize_history(history: list[dict]) -> str:
    conversation_history = "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in history
    )
    prompt = f"""
                    Summarize the conversation below.

                    Preserve:
                    - important facts
                    - entities
                    - user references
                    - previous questions
                    - previous answers

                    Keep the summary concise.

                    Conversation:
                     {conversation_history}
                """
    response = llm.invoke(prompt)
    return response.content.strip()
