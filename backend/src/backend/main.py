
from fastapi import APIRouter

router = APIRouter(
            prefix="/items",
            tags=["Items"]
        )

@router.get("/health")
async def read_health():
    return {"status": "healthy"}