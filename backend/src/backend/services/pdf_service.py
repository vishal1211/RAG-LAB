from pypdf import PdfReader
from io import BytesIO
from ..api.exceptions import DocumentProcessingError


def extract_pdf_pages(file_bytes: bytes) -> list[dict]:

    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages = []
        for count, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                pages.append({"page": count, "text": text})
        return pages
    except Exception as exc:
        raise DocumentProcessingError("Failed to process PDF document.") from exc
