from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    retrieval_k: int = 3
    retrieval_distance_threshold: float = 1.25
    model_name: str = "openai/gpt-oss-120b"
    groq_api_key: str
    ollama_api_key: str | None = None
    google_api_key: str | None = None
    huggingface_api_key: str | None = None
    memory_history_limit: int = 10
    data_dir: str = "data"
    vector_store_path: str = "data/vector_store"
    memory_db_path: str = "data/conversation_memory.db"
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
