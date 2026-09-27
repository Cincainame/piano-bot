from sqlalchemy import select

from database import Attendance, Student, create_tables, session_scope

attendance_data = [
    {"studentName": "Lo Ze Xuan", "term": "Sep, Oct, Nov", "absent_date": "10/10, 28/11", "replacement_date": ""}
]


def seed_attendance() -> int:
    create_tables()
    inserted_count = 0
    with session_scope() as session:
        for slot in attendance_data:
            student_id = session.scalar(
                select(Student.id).where(Student.name == slot["studentName"])
            )
            if student_id is None:
                raise ValueError(
                    f'No student found with name {slot["studentName"]!r}'
                )

            session.add(
                Attendance(
                    student_id=student_id,
                    term=slot["term"],
                    absent_date=slot["absent_date"],
                    replacement_date=slot["replacement_date"],
                )
            )
            inserted_count += 1

    return inserted_count


if __name__ == "__main__":
    count = seed_attendance()
    print(f"Inserted {count} attendance rows.")