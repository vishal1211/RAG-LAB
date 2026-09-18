from .agent_controller import decide_next_action
from .retriever import retrieve_documents
from .corrective_retrieval import corrective_retrieve
from .generator import generate_answer
from .answer_verifier import verify_answer


def run_agentic_rag(
    query: str, retrieval_query: str, strategy: str, history: list[dict], summary: str
):
    retrieval_available = False
    retrieval_relevant = None

    answer_generated = False
    answer_supported = None

    correction_attempted = False

    results = []
    answer = None
    search_text = None
    trace = []
    max_steps = 5

    for _ in range(max_steps):

        action = decide_next_action(
            retrieval_available=retrieval_available,
            retrieval_relevant=retrieval_relevant,
            answer_generated=answer_generated,
            answer_supported=answer_supported,
            correction_attempted=correction_attempted,
        )
        trace.append(action)
        print("Agent action:", action)

        if action == "retrieve":

            search_text, results, is_relevant = retrieve_documents(
                retrieval_query, use_hyde=strategy == "hyde"
            )

            retrieval_available = True
            retrieval_relevant = is_relevant

        elif action == "correct":

            correction_attempted = True

            correction_result = corrective_retrieve(
                query=retrieval_query, strategy=strategy
            )

            results = correction_result["results"]
            search_text = correction_result["search_text"]

            retrieval_available = True
            retrieval_relevant = correction_result["is_relevant"]

            answer = None
            answer_generated = False
            answer_supported = None

        elif action == "generate":

            if not results:
                break

            answer = generate_answer(
                query=query, retrieved_results=results, history=history, summary=summary
            )

            answer_generated = True

            answer_supported = verify_answer(
                query=query, answer=answer, retrieved_results=results
            )

        elif action == "finish":
            break

    if not answer or answer_supported is not True:
        answer = "I don't know based on the provided document."

    return {
        "answer": answer,
        "results": results,
        "search_text": search_text,
        "answer_supported": answer_supported,
        "trace": trace,
    }
