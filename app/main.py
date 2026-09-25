from fastapi import FastAPI

from app.routers import attendance

app = FastAPI(title="Piano Bot API")

app.include_router(attendance.router)


@app.get("/")
def root():
    return {"message": "Piano Bot API is running"}
