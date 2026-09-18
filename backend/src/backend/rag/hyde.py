from langchain_groq import ChatGroq

from ..settings import settings

llm = ChatGroq(model=settings.model_name, api_key=settings.groq_api_key, temperature=0)


def generate_hypothetical_document(query: str) -> str:
    promt = f"""
                Generate a concise hypothetical document passage that could contain
                the answer to the question below.

                Do not answer conversationally.
                Do not mention that the passage is hypothetical.
                Return only the passage.

                Question:
                {query}
                """
    hypothetical_document = llm.invoke(promt).content.strip()
    return hypothetical_document
