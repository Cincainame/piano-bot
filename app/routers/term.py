from datetime import date

from fastapi import APIRouter, HTTPException

from app.schemas import TermCreate, TermResponse
from app.services.supabase_client import supabase
from app.services.term import get_term_db, add_term_db

router = APIRouter(prefix="/term", tags=["term"])

@router.post("/{studentId}", response_model=TermResponse, status_code=201)
def create_term(studentId: int):
    """
    Create a new term for the specified student.
    """
    existing_record = get_term_db(studentId)

    # current month integer
    current_month = date.today().month
    current_year = date.today().year
    term_month = [((current_month - 1 + i) % 12) + 1 for i in range(3)]  # next three months
    record = TermCreate(student_id=studentId, year=current_year, term=term_month)

    # only add term when last term month is less than current month or if no existing record
    if not existing_record or existing_record["term"][-1] < current_month: 
        return add_term_db(record)
    else:
        raise HTTPException(status_code=400, detail="Cannot add term for this student yet. Last term month is greater than or equal to current month.")