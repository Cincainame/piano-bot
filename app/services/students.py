
from http.client import HTTPException

from app.schemas import StudentResponse
from app.services.supabase_client import supabase

def get_all_students() -> list[StudentResponse]:
    data = supabase.table("student").select("*").execute().data
    return [StudentResponse(**student) for student in data]

def get_student(student_id: int) -> StudentResponse:
    data = (
        supabase.table("student")
        .select("*")
        .eq("id", student_id)
        .execute()
        .data
    )
    if not data:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentResponse(**data[0])

def get_student_by_name(name: str) -> StudentResponse:
    data = (
        supabase.table("student")
        .select("*")
        .ilike("name", f"%{name}%")
        .execute()
        .data
    )
    if not data:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentResponse(**data[0])