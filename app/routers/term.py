from datetime import date

from fastapi import APIRouter, HTTPException

from app.schemas import TermResponse
from app.services import term as service
router = APIRouter(prefix="/term", tags=["term"])

@router.get("/find_term_by_month", response_model=TermResponse | None, status_code=200)
def find_term_by_month(studentId: int, month: int | None = None, year: int | None = None):
    """
    Get the term for the specified student for the given month and year if specified.
    """
    term = service.find_term_id_by_month(studentId, month, year)
    if not term:
        raise HTTPException(status_code=404, detail="Term not found for the student")
    return term



@router.post("/{studentId}", response_model=TermResponse, status_code=201)
def create_term(studentId: int):
    """
    Create a new term for the specified student.
    """
    
    return service.add_term_if_needed(studentId)

