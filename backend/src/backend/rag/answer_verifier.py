from langchain_groq import ChatGroq
from pydantic import BaseModel

from ..settings import settings

llm = ChatGroq(model=settings.model_name, api_key=settings.groq_api_key, temperature=0)


class AnswerVerification(BaseModel):
    supported: bool


structured_llm = llm.with_structured_output(AnswerVerification, method="json_schema")


def verify_answer(query: str, answer: str, retrieved_results) -> bool:

    context = "\n\n".join([doc.page_content for doc, _ in retrieved_results])
    prompt = f"""
                Determine whether the answer is supported by the provided document context.

                Return only one word:
                yes
                no

                Question:
                {query}

                Context:
                {context}

                Answer:
                {answer}
            """
    response = structured_llm.invoke(prompt)

    return response.supported
