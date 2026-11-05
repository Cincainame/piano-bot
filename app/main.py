import sys
from pathlib import Path

from fastapi import FastAPI

# Put the project root on sys.path so `from app.routers import ...` (and the
# `from bot.config import ...` inside the services) resolve no matter where
# uvicorn is launched from -- e.g. `uvicorn app.main:app` from the repo root,
# `uvicorn main:app` from inside app/, or `python app/main.py`. Without this,
# launching from anywhere but the project root raises ModuleNotFoundError.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from app.routers import attendance, students, term

app = FastAPI(title="Piano Bot API")

app.include_router(students.router)
app.include_router(attendance.router)
app.include_router(term.router)


@app.get("/")
def root():
    return {"message": "Piano Bot API is running"}
