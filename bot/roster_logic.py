from datetime import datetime

from sqlalchemy import select

from .database import Student, session_scope


def read_timetable():
    with session_scope() as session:
        students = session.scalars(
            select(Student).order_by(Student.day_of_week, Student.start_time)
        ).all()
    return [
        {
            "day": student.day_of_week,
            "start": student.start_time,
            "end": student.end_time,
            "students": student.name,
        }
        for student in students
    ]

def timetable_to_text():
    lines = []
    timetable = read_timetable()

    for lesson in timetable:
        day = lesson["day"]
        start = lesson["start"]
        end = lesson["end"]
        students = lesson["students"]

        # Convert HH:MM to 12-hour format without leading zero
        def format_time(time_str):
            hour, minute = map(int, time_str.split(":"))

            period = "am" if hour < 12 else "pm"
            display_hour = hour % 12
            if display_hour == 0:
                display_hour = 12

            if minute == 0:
                return f"{display_hour}{period}"
            else:
                return f"{display_hour}{minute:02d}{period}"

        start_text = format_time(start)
        end_text = format_time(end)


        lines.append(
            f"{day} {start_text}-{end_text} {students}"
        )

    return "\n".join(lines)

def add_student_to_student_roster(name: str, start_time: str, end_time: str):
    start_time, end_time = normalize_time_range(start_time, end_time)
    with session_scope() as session:
        students = session.scalars(
            select(Student).where(Student.day_of_week == "Saturday")
        ).all()
        timetable = [
            {
                "day": student.day_of_week,
                "start": student.start_time,
                "end": student.end_time,
                "students": student.name,
            }
            for student in students
        ]
        conflict = check_time_conflict(timetable, start=start_time, end=end_time)

        if conflict:
            raise ValueError(
                f"Time slot {start_time}-{end_time} is already taken by "
                f"{conflict[0]['students']}."
            )

        session.add(
            Student(
                name=name,
                start_time=start_time,
                end_time=end_time,
                day_of_week="Saturday",
            )
        )



def check_time_conflict(timetable, start, end):
    new_start = datetime.strptime(start, "%H:%M").time()
    new_end = datetime.strptime(end, "%H:%M").time()

    conflicts = []

    for lesson in timetable:
        existing_start = datetime.strptime(
            lesson["start"], "%H:%M"
        ).time()

        existing_end = datetime.strptime(
            lesson["end"], "%H:%M"
        ).time()

        if new_start < existing_end and new_end > existing_start:
            conflicts.append(lesson)

    return conflicts

def normalize_time_range(start: str, end: str) -> tuple[str, str]:

    start = start.strip().lower()
    end = end.strip().lower()

    # Normalize spaces
    start = " ".join(start.split())
    end = " ".join(end.split())

    # If start has no AM/PM, inherit it from end
    if "am" not in start and "pm" not in start:
        if "am" in end:
            start += " am"
        elif "pm" in end:
            start += " pm"

    # If end has no AM/PM, inherit it from start
    if "am" not in end and "pm" not in end:
        if "am" in start:
            end += " am"
        elif "pm" in start:
            end += " pm"

    def parse(value):
        for fmt in ("%I:%M %p", "%I %p", "%H:%M"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass

        raise ValueError(f"Invalid time: {value}")

    start_dt = parse(start)
    end_dt = parse(end)

    return (
        start_dt.strftime("%H:%M"),
        end_dt.strftime("%H:%M")
    )