from datetime import date

from fastapi import HTTPException

from app.schemas import TermCreate, TermResponse
from app.services.supabase_client import supabase

def get_term_db(student_id: int):
    data = (
        supabase.table("term")
        .select("*")
        .eq("student_id", student_id)
        .execute()
        .data
    )
    if not data:
        return None
    return data[0]

def add_term_db(record: TermCreate):
    data = supabase.table("term").insert(record.model_dump()).execute().data
    if not data:
        raise HTTPException(status_code=400, detail="Insert failed")
    return data[0]


def add_term_if_needed(student_id: int):
    existing_record = get_term_db(student_id)

    # current month integer
    current_month = date.today().month
    current_year = date.today().year
    term_month = [((current_month - 1 + i) % 12) + 1 for i in range(3)]  # next three months
    record = TermCreate(student_id=student_id, year=current_year, term=term_month)

    # only add term when last term month is less than current month or if no existing record
    if not existing_record or existing_record["term"][-1] < current_month: 
        return add_term_db(record)
    else:
        raise HTTPException(status_code=400, detail="Cannot add term for this student yet. Last term month is greater than or equal to current month.")  


def get_latest_term_id(student_id: int) -> int | None:
    query = supabase.table("term").select("id")

    if student_id is not None:
        query = query.eq("student_id", student_id)

    result = (
        query
        .order("year", desc=True)
        .order("id", desc=True)
        .limit(1)
        .execute()
    )

    if not result.data:      # table is empty
        new_term = add_term_if_needed(student_id)
        return new_term["id"]
    return result.data[0]["id"]


def find_term_id_by_month(
    student_id: int,
    month: int | None = None,
    year: int | None = None,
) -> TermResponse | None:
    year = year or date.today().year

    query = (
        supabase.table("term")
        .select("*")
        .eq("student_id", student_id)
        .eq("year", year)
    )

    if month is not None:
        query = query.contains("term", [str(month)])

    result = query.order("id", desc=True).limit(1).execute()

    if not result.data:
        return None
    return result.data[0]