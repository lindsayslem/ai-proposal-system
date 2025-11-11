from fastapi import APIRouter

router = APIRouter(prefix="/proposals", tags=["proposals"])

@router.get("/")
async def list_proposals():
    return {"proposals": []}