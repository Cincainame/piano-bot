from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class ListingStudentIds(BaseModel):
    ids: list[int] = Field(max_length=200)

class AbsenceBase(BaseModel):
    term_id: Optional[int] = None
    absent_date: date

class AbsenceCreate(AbsenceBase):
    student_id: int

class AbsenceResponse(AbsenceBase):
    id: int
    student_id: int

    model_config= ConfigDict(from_attributes=True)

class SkippedStudent(BaseModel):
    student_id: int
    name: str
    reason: str

class TeacherAbsenceResponse(BaseModel):
    created: list[AbsenceResponse]
    skipped: list[SkippedStudent]

class AttendanceBase(BaseModel):
    student_id: int
    term: str
    absent_date: date
    replacement_date: Optional[date] = None

class TermBase(BaseModel):
    student_id: int
    year: int
    term: list[int]


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

class TermCreate(TermBase):
    pass

class TermResponse(TermBase):
    id: int
    student_id: int
    year: int
    term: list[int]
    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    name: str
    start_time: time
    end_time: time
    phone_no: str
    day_of_week: str


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True

class ReplacementBase(BaseModel):
    term_id: int
    replacement_date: date


class ReplacementCreate(ReplacementBase):
    pass
    is_waived: bool = False


class ReplacementResponse(ReplacementBase):
    id: int

    class Config:
        from_attributes = True


