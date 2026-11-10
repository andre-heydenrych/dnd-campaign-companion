from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.routers import items

app = FastAPI(title="D&D Campaign Companion API")
app.include_router(items.router)

@app.get("/health")
def health():
    return {"status": "ok"}