from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    stored: bool
    duplicate: bool
    file_hash: str
    chunks_stored: int | None = None
    message: str


class SourceResponse(BaseModel):
    filename: str | None = None
    page: int | None = None
    content: str
    distance: float


class SearchResponse(BaseModel):
    original_query: str
    retrieval_query: str
    strategy: str
    search_text: str | None = None
    answer: str
    is_supported: bool | None = None
    agent_trace: list[str]
    sources: list[SourceResponse]
