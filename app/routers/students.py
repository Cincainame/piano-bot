from datetime import date

from fastapi import APIRouter, HTTPException

from app.schemas import StudentResponse
from app.services import students as service

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/", response_model=list[StudentResponse], status_code=201)
def get_all_students():
    """
    Get all students.
    """
    return service.get_all_students()

@router.get("/{student_id}", response_model=StudentResponse, status_code=200)
def get_student(student_id: int):
    """
    Get a student by ID.
    """
    return service.get_student(student_id)