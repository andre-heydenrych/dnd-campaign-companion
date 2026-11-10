from fastapi import FastAPI
from app.routers import items

app = FastAPI(title="D&D Campaign Companion API")
app.include_router(items.router)

@app.get("/health")
def health():
    return {"status": "ok"}