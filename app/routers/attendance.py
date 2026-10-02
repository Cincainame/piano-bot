from app.services import attendance as attendance_services
from app.services import students as student_services
from fastapi import APIRouter, HTTPException

from app.schemas import AbsenceBase, AbsenceCreate, AbsenceResponse, AttendanceResponse, SkippedStudent, TeacherAbsenceResponse
from app.services.supabase_client import supabase

router = APIRouter(prefix="/attendance", tags=["attendance"])

@router.get("/get-student-attendance/{student_id}", response_model=list[str], status_code=200)
def get_student_attendance(student_id: int, term_id):
    return attendance_services.get_student_attendance(student_id, term_id)

@router.post("/report-student-absence/{student_id}", response_model=AbsenceResponse, status_code=201)
def report_student_absence(student_id: int, body: AbsenceBase):
    record = AbsenceCreate(student_id=student_id, **body.model_dump())
    return attendance_services.create_absence(record)

@router.post("/report-teacher-absence", response_model=TeacherAbsenceResponse, status_code=201)
def report_teacher_absence(body: AbsenceBase):
    all_students = student_services.get_all_students()
    created, skipped = [], []
    for student in all_students:
        record = AbsenceCreate(student_id=student.id, **body.model_dump())
        try:
            created.append(attendance_services.create_absence(record))
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
