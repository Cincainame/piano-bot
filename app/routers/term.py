from datetime import date

from fastapi import APIRouter, HTTPException

from app.schemas import TermCreate, TermResponse
from app.services.term import add_term_if_needed, get_term_db, add_term_db

router = APIRouter(prefix="/term", tags=["term"])

@router.post("/{studentId}", response_model=TermResponse, status_code=201)
def create_term(studentId: int):
    """
    Create a new term for the specified student.
    """
    add_term_if_needed(studentId)