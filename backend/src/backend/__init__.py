from fastapi import FastAPI, Request

from .main import router
from .upload import upload_router
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse

app = FastAPI(title="Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://rag-lab-lovat.vercel.app/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(upload_router)


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