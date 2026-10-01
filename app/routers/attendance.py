from app.services.attendance import create_absence
from app.services.students import get_all_students
from fastapi import APIRouter, HTTPException

from app.schemas import AbsenceBase, AbsenceCreate, AbsenceResponse, AttendanceCreate, AttendanceUpdate, AttendanceResponse, SkippedStudent, TeacherAbsenceResponse
from app.services.supabase_client import supabase

router = APIRouter(prefix="/attendance", tags=["attendance"])

@router.post("/report-student-absence/{student_id}", response_model=AbsenceResponse, status_code=201)
def report_student_absence(student_id: int, body: AbsenceBase):
    record = AbsenceCreate(student_id=student_id, **body.model_dump())
    return create_absence(record)

@router.post("/report-teacher-absence", response_model=TeacherAbsenceResponse, status_code=201)
def report_teacher_absence(body: AbsenceBase):
    all_students = get_all_students()
    created, skipped = [], []
    for student in all_students:
        record = AbsenceCreate(student_id=student.id, **body.model_dump())
        try:
            created.append(create_absence(record))
        except HTTPException as e:
            
            if e.status_code == 400:
                skipped.append(SkippedStudent(
                    student_id=student.id,
                    name=student.name,
                    reason=e.detail,
                ))
            else:
                raise
    return TeacherAbsenceResponse(created=created, skipped=skipped)
