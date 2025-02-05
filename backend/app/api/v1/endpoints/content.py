from fastapi import APIRouter

router = APIRouter()

@router.get("/content")
def read_content():
    return {"message": "Content endpoint"} 