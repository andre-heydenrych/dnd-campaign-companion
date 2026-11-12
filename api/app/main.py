from fastapi import FastAPI

from app.routers import accounts

app = FastAPI(title="D&D Campaign Companion API")
app.include_router(accounts.router)


@app.get("/health")
def health():
    return {"status": "ok"}
