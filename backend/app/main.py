from fastapi import FastAPI
from app.api.v1.endpoints import content

app = FastAPI()

# API 라우터 등록
app.include_router(content.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the CEO Blog Editor API!"} 