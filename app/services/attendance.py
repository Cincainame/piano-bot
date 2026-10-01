from datetime import date

from fastapi import HTTPException

from app.schemas import AbsenceCreate
from app.services.supabase_client import supabase
from app.services.term import get_latest_term_id

def create_absence(record: AbsenceCreate):
    if record.term_id is None or record.term_id == 0:
        # If term_id is not provided, fetch the latest term_id for the student
        latest_term_id = get_latest_term_id(record.student_id)
        if latest_term_id is None:
            raise HTTPException(status_code=400, detail="No term found for the student")
        record.term_id = latest_term_id

    if check_existing_absence(record.student_id, record.term_id, record.absent_date):
        raise HTTPException(status_code=400, detail="Absence record already exists for this student, term, and date.")

    data = supabase.table("absence").insert(record.model_dump(mode="json")).execute().data
    if not data:
        raise HTTPException(status_code=400, detail="Insert failed")
    return data[0]

def check_existing_absence(student_id: int, term_id: int, absent_date: date) -> bool:
    data = (
        supabase.table("absence")
        .select("id")
        .eq("student_id", student_id)
        .eq("term_id", term_id)
        .eq("absent_date", absent_date)
        .execute()
        .data
    )
    return len(data) > 0
