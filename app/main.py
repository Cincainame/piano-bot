from fastapi import FastAPI

from app.routers import attendance, students, term

app = FastAPI(title="Piano Bot API")

app.include_router(students.router)
app.include_router(attendance.router)
app.include_router(term.router)


@app.get("/")
def root():
    return {"message": "Piano Bot API is running"}
