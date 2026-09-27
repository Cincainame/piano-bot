from http.client import HTTPException

from app.schemas import TermCreate
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