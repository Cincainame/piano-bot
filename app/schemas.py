from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class AttendanceBase(BaseModel):
    student_id: int
    term: str
    absent_date: date
    replacement_date: Optional[date] = None


class AttendanceCreate(AttendanceBase):
    """Body for POST /attendance — fields the client provides."""
    pass


class AttendanceUpdate(BaseModel):
    """Body for PATCH /attendance/{id} — every field is optional."""
    student_id: Optional[int] = None
    term: Optional[str] = None
    absent_date: Optional[date] = None
    replacement_date: Optional[date] = None


class AttendanceResponse(AttendanceBase):
    """Full row as returned by Supabase — includes DB-managed columns."""
    id: int
    student_id: int
    term: str
    absent_date: str
    replacement_date: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
