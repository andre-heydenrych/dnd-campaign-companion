from fastapi import FastAPI

app = FastAPI(title="D&D Campaign Companion API")

@app.get("/health")
def health():
    return {"status": "ok"}