from fastapi import FastAPI, Request

from .main import router
from .upload import upload_router

from fastapi.responses import JSONResponse

app = FastAPI(title="Backend API", version="1.0.0")

app.include_router(router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")


from  .api.exceptions import (
    DocumentProcessingError,
    RetrievalError,
    GenerationError,
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Backend API!"}



@app.exception_handler(DocumentProcessingError)
async def document_processing_error_handler(
    request: Request,
    exc: DocumentProcessingError
):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(RetrievalError)
async def retrieval_error_handler(
    request: Request,
    exc: RetrievalError
):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


@app.exception_handler(GenerationError)
async def generation_error_handler(
    request: Request,
    exc: GenerationError
):
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc)}
    )