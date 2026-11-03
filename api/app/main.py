from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.routers import items

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)   # create tables on startup
    yield

app = FastAPI(title="D&D Campaign Companion API", lifespan=lifespan)
app.include_router(items.router)

@app.get("/health")
def health():
    return {"status": "ok"}