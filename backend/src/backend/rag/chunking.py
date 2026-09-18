from ..settings import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
)


def create_documents(
    pages: list[dict], file_hash: str, filename: str
) -> list[Document]:
    documents = []
    document_text = ""

    for page in pages:
        document_text += page["text"]

    text_chunks = text_splitter.split_text(document_text)

    for page_number, chunk in enumerate(text_chunks, start=1):
        document = Document(
            page_content=chunk,
            metadata={
                "source": filename,
                "page": page_number,
                "file_hash": file_hash,
            },
        )
        documents.append(document)

    return documents
