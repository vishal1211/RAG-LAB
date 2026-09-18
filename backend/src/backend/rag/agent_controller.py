from langchain_groq import ChatGroq

from ..settings import settings

llm = ChatGroq(model=settings.model_name, api_key=settings.groq_api_key, temperature=0)


def decide_next_action(
    retrieval_available: bool,
    retrieval_relevant: bool | None = None,
    answer_generated: bool = False,
    answer_supported: bool | None = None,
    correction_attempted: bool = False,
) -> str:

    if not retrieval_available:
        return "retrieve"

    if retrieval_relevant is False:
        if correction_attempted:
            return "finish"

        return "correct"

    if retrieval_relevant is True and not answer_generated:
        return "generate"

    if answer_generated and answer_supported is True:
        return "finish"

    if answer_generated and answer_supported is False:
        if correction_attempted:
            return "finish"

        return "correct"

    return "finish"
