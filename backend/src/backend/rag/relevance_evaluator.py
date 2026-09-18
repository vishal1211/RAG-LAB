from langchain_groq import ChatGroq
from pydantic import BaseModel

from ..settings import settings

llm = ChatGroq(model=settings.model_name, api_key=settings.groq_api_key, temperature=0)


class RelevanceDecision(BaseModel):
    relevant: bool


structured_llm = llm.with_structured_output(RelevanceDecision, method="json_schema")


def is_document_relevant(query: str, document_text: str) -> bool:

    prompt = f"""
                Determine whether the document content contains information
                that is useful for answering the query.

                Return only one word:
                yes
                no

                Query:
                {query}

                Document:
                {document_text}
            """

    response = structured_llm.invoke(prompt)
    return response.relevant
