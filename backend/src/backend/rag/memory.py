import sqlite3

from .memory_summary import summarize_history

DATABASE_PATH = "conversation_memory.db"


def initialize_memory():
    # Create the conversation_memory table if it doesn't exist
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS conversation_memory (
                session_id TEXT,
                role TEXT,
                content TEXT
            )
        """)
        connection.execute(
            "CREATE TABLE IF NOT EXISTS conversation_summaries(session_id TEXT PRIMARY KEY, summary TEXT NOT NULL)"
        )


def get_history(session_id: str, memory_history_limit: int) -> list[dict]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(
            "SELECT role, content FROM conversation_memory WHERE session_id = ? ORDER BY rowid DESC LIMIT ?",
            (session_id, memory_history_limit),
        ).fetchall()
    rows.reverse()  # Reverse the rows to maintain chronological order
    return [
        {"role": role, "content": content} for role, content in rows
    ]  # Reverse to maintain chronological order


def add_message(session_id: str, role: str, content: str) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            "INSERT INTO conversation_memory (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )


def get_summary(session_id: str) -> str | None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            "SELECT summary FROM conversation_summaries WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    return row[0] if row else None


def save_summary(session_id: str, summary: str) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            "INSERT OR REPLACE INTO conversation_summaries (session_id, summary) VALUES (?, ?)",
            (session_id, summary),
        )


def compact_memory(session_id: str, keep_recent: int = 10) -> None:

    all_history = get_history(session_id=session_id, memory_history_limit=1000)

    if len(all_history) <= keep_recent:
        return

    older_messages = all_history[:-keep_recent]

    existing_summary = get_summary(session_id)

    summary_input = []

    if existing_summary:
        summary_input.append(
            {"role": "system", "content": f"Previous summary: {existing_summary}"}
        )

    summary_input.extend(older_messages)

    updated_summary = summarize_history(summary_input)

    save_summary(session_id=session_id, summary=updated_summary)


initialize_memory()
