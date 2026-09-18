from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from ..settings import settings

embedding_model = HuggingFaceEmbeddings(
    model_name=settings.embedding_model,
    model_kwargs={"token": settings.huggingface_api_key},
)

vector_store = Chroma(
    collection_name="rag_documents",
    persist_directory=settings.vector_store_path,
    embedding_function=embedding_model,
)
