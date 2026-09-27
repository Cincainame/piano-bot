from fastapi import APIRouter, HTTPException

from app.schemas import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.services.supabase_client import supabase

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("", response_model=list[AttendanceResponse])
def list_attendance():
    return supabase.table("attendance").select("*").limit(50).execute().data


@router.get("/{record_id}", response_model=AttendanceResponse)
def get_attendance(record_id: int):
    data = (
        supabase.table("attendance")
        .select("*")
        .eq("id", record_id)
        .execute()
        .data
    )
    if not data:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return data[0]


@router.post("", response_model=AttendanceResponse, status_code=201)
def create_attendance(record: AttendanceCreate):
    data = supabase.table("attendance").insert(record.model_dump()).execute().data
    if not data:
        raise HTTPException(status_code=400, detail="Insert failed")
    return data[0]


@router.patch("/{record_id}", response_model=AttendanceResponse)
def update_attendance(record_id: int, updates: AttendanceUpdate):
    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    data = (
        supabase.table("attendance")
        .update(update_data)
        .eq("id", record_id)
        .execute()
        .data
    )
    if not data:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return data[0]
