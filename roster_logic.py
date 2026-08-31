import json

CONST_TIMETABLE_FILE = "student_roster.json"

def read_timetable_json():
    with open(CONST_TIMETABLE_FILE, "r") as f:
        timetable = json.load(f)
    return timetable

def timetable_to_text():
    lines = []
    timetable = read_timetable_json()

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