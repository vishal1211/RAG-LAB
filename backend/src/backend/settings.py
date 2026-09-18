from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_store_path: str = "vector_store"
    retrieval_k: int = 3
    retrieval_distance_threshold: float = 1.0
    model_name: str = "openai/gpt-oss-120b"
    groq_api_key: str
    ollama_api_key: str | None = None
    google_api_key: str | None = None
    huggingface_api_key: str
    memory_history_limit: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
