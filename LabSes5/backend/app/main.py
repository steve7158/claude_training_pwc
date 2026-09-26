from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.routers import notes, patients, summarize  # noqa: E402

app = FastAPI(title="Banner Health Clinical Assistant (Prototype)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router)
app.include_router(summarize.router)
app.include_router(notes.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
