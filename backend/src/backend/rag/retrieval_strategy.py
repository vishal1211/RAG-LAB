from langchain_groq import ChatGroq

from ..settings import settings
from pydantic import BaseModel
from typing import Literal

llm = ChatGroq(model=settings.model_name, api_key=settings.groq_api_key, temperature=0)


class RetrievalStrategy(BaseModel):
    strategy: Literal["normal", "hyde"]


structured_llm = llm.with_structured_output(RetrievalStrategy, method="json_schema")


def choose_retrieval_strategy(query: str) -> str:
    prompt = f"""
                Classify the query into one retrieval strategy.

                Return only one of these values:
                normal
                hyde

                Use "hyde" when the query is vague, short, abstract,
                or may benefit from generating a hypothetical document first.

                Use "normal" when the query is already specific and clear.

                Query:
                {query}
            """

    response = structured_llm.invoke(prompt)
    return response.strategy
