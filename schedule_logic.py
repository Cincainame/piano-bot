import calendar
import json
from datetime import date
import os
from typing import Optional, TypedDict, List, Dict, Any

from dotenv.main import logger

lessons_per_term = 11
today = date.today()
year = today.year

month_str_to_num = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

class RosterEntry(TypedDict):
    name: str
    day_time: str
    months: list[str]
    year: int
    attended_dates: list[str]
    replacement_dates: list[str]
    unclear_dates: list[str]

class TermUpdateResult(TypedDict):
    action: str
    schedule_text: str
    past_absences: list[str]
    unclear_dates: list[str]

class StudentTerm(TypedDict):
    name: str
    day_time: str
    months: list[str]
    year: int
    attended_dates: list[str]
    replacement_dates: list[str]
    unclear_dates: list[str]

class StudentData(TypedDict):
    parent_number: str
    terms: list[StudentTerm]


DATA_FILE = "./student_data.json" 
STUDENT_FILE = "./student_roster.txt"  # for storing parent numbers and other info

def _load_all():
    with open(DATA_FILE) as f:
        return json.load(f)

def _save_all(data):
    # write to a temp file first, then swap — avoids a corrupted file
    # if the bot crashes mid-write
    tmp_file = DATA_FILE + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_file, DATA_FILE)
    

def parse_roster() -> dict[str, str]:

    roster = {}
    with open(STUDENT_FILE) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 3:
                continue
            day_time = " ".join(parts[:2])
            name = " ".join(parts[2:]).strip()

            roster[name] = day_time
    return roster

def build_roster_block() -> str:
    """Turns {name: day_time} into readable 'day_time name' lines for the prompt."""
    roster = parse_roster()  # {name: day_time}
    lines = [f"{day_time} {name}" for name, day_time in roster.items()]

    return "\n".join(lines)

def load_student(name: str) -> StudentData:
    data: dict[str, StudentData] = _load_all()
    if name not in data:
        raise ValueError(f"Student '{name}' not found in student_data.json")
    return data[name]

def daytoWeekdayNumber(day: str) -> int:
    return list(calendar.day_name).index(day)

def monthFormatter(monthList: list[str]) -> list[int]:
    month_abbrs = [m.strip()[:3].title() for m in monthList]
    return [month_str_to_num[m] for m in month_abbrs]

def dateFormatter(raw_date: str) -> date:
    day_str, month_str = raw_date.strip().split("-")
    return date(year, int(month_str), int(day_str))

def statusPicker(d: date) -> str:
    return "✅" if d < today else "⭐"

def find_matching_dates(day_index: int, month_in_nums: list[int], year: int) -> list[tuple[date, str]]:
    matching_dates = []
    for month in month_in_nums:
        for week in calendar.monthcalendar(year, month):
            day = week[day_index]
            if day != 0:
                d = date(year, month, day)
                matching_dates.append((d, statusPicker(d)))
    return matching_dates

def compute_past_absences(day_time: str, months: list[str], year: int, attended_dates: list[str], replacement_dates: list[str], specified_absent_dates: list[str]) -> list[str]:
    all_expected = find_matching_dates(daytoWeekdayNumber(day_time.split(" ")[0]), monthFormatter(months), year)
    today = date.today()
    known = set(attended_dates) | set(replacement_dates) | set(specified_absent_dates)
    return [d.strftime("%d-%m") for d, _ in all_expected if d < today and d.strftime("%d-%m") not in known]

def update_terms_from_photo(students: list) -> list:
    """
    students: list of dicts from extract_from_photo.
    Returns a list of per-student results, including any that failed,
    so nothing silently disappears.
    """
    results = []
    for entry in students:
        name = entry.get("name", "unknown")
        try:
            result = update_term_from_photo(
                name=name,
                day_time=entry["day_time"],
                months=entry["months"],
                year=entry["year"],
                attended_dates=entry.get("attended_dates", []),
                replacement_dates=entry.get("replacement_dates", []),
                unclear_dates=entry.get("unclear_dates", [])
            )
            result["name"] = name
            result["ok"] = True
            results.append(result)
        except ValueError as e:
            results.append({"name": name, "ok": False, "error": str(e)})
        except Exception:
            logger.exception(f"Failed processing {name} from photo")
            results.append({"name": name, "ok": False, "error": "unexpected error, check logs"})
    return results

def update_term_from_photo(
    name: str,
    day_time: str,
    months: list[str],
    year: int,
    attended_dates: list[str],
    replacement_dates: list[str],
    unclear_dates: Optional[list[str]] = None
) -> TermUpdateResult:
    unclear_dates = unclear_dates or []
    
    # load from student data 
    data = _load_all()

    if name not in data:
        raise ValueError(
            f"'{name}' isn't in student_data.json yet. Add them with a parent_number first."
        )

    student = data[name]
    student.setdefault("terms", [])

    existing = _find_term(student, months, year)
    if existing is None:
        existing = {
            "year": year,
            "months": months,
            "day_time": day_time,
            "specified_absent_dates": [],
            "replacement_dates": [],
            "special_slots": []
        }
        student["terms"].append(existing)
        action = "created"
    else:
        action = "updated"

    # Merge replacement dates, no duplicates
    for d in replacement_dates:
        if d not in existing["replacement_dates"]:
            existing["replacement_dates"].append(d)
    existing["day_time"] = day_time  # allow correction if it changed

    computed_absences = compute_past_absences(
        day_time, months, year, attended_dates,
        existing["replacement_dates"], existing["specified_absent_dates"]
    )

    _save_all(data)

    return {
        "action": action,
        "schedule_text": _render_schedule(name, existing),
        "past_absences": computed_absences,   # possible unreported absences — needs your confirmation
        "unclear_dates": unclear_dates    # Gemini couldn't read these — needs your eyes
    }

def remove_absent_class(matchingDates: list[tuple[date, str]], absentList: list[str]) -> list[tuple[date, str]]:
    for d in absentList:
        date_to_remove = dateFormatter(d)
        matchingDates = [(dd, s) for (dd, s) in matchingDates if dd != date_to_remove]
    return matchingDates

def build_full_schedule(name: str, day_time: str, term: str, year: int, specific_absent_list=None, replace_list=None, special_list=None) -> str:
    """
    Main entry point. absent_list / replace_list: lists of 'dd-mm' strings.
    special_list: list of (info_string, slot_index) tuples.
    """
    absent_list = []
    specific_absent_list = specific_absent_list or []
    replace_list = replace_list or []
    special_list = special_list or []

    student = load_student(name)
    day_time = student["day_time"]
    term = student["term"]
    day = day_time.strip().split(" ")[0]

    months = [m.strip() for m in term.strip().split(',')]

    dates = find_matching_dates(daytoWeekdayNumber(day), monthFormatter(months), year)
    absent_list= compute_past_absences(day_time, months, year, student.get("attended_dates", []), student.get("replacement_dates", []))
    aggregate_absent_list = specific_absent_list + absent_list
    dates_after_absent = remove_absent_class(dates, aggregate_absent_list)

    replacedDates = [(dateFormatter(d), statusPicker(dateFormatter(d))) for d in replace_list]
    replaced_date_values = set(d for d, _ in replacedDates)

    all_dates = sorted(dates_after_absent + replacedDates, key=lambda x: x[0])
    for info, idx in special_list:
        all_dates.insert(idx - 1, (info, "✅"))

    lines = [f"{name} Piano Semester ({term})", day_time]
    lessonCount = 0
    for d, status in all_dates:
        if lessonCount < lessons_per_term:
            lessonCount += 1
            note = " (replacement)" if d in replaced_date_values else ""
            date_str = d if isinstance(d, str) else d.strftime('%d %B')
            lines.append(f"#{lessonCount} - {date_str} {status}{note}")
        else:
            lines.append(f"Backup Date - {d.strftime('%d %B')}")

    replacement = 0
    while lessonCount < lessons_per_term:
        replacement += 1
        lessonCount += 1
        lines.append(f"#{lessonCount} - *pending replacement*")

    lines.append("")
    for absent in aggregate_absent_list:
        lines.append(f"Absent Date - {dateFormatter(absent).strftime('%d %B')} 🔴")
    lines.append("")

    if replacement:
        lines.append(f"Good morning! For {name}'s {term} semester, we still have *{replacement}* "
                      f"replacement class to arrange. Let me know when you're free, and we'll find a time that works. 😁")
    else:
        lines.append(f"Good morning! This is {name}'s {term} semester schedule. "
                      f"Do let me know if you have any questions. 😁")

    return "\n".join(lines)

def build_simple_absence_text(absent_date_str: str, present_date_str: str) -> str:
    return (f"⚠️Good morning! Just a quick note - there will be no class on {absent_date_str}. "
            f"Our next class will be on {present_date_str}.😁")

def _find_term(student: StudentData, months: list[str], year: Optional[int] = None) -> Optional[StudentTerm]:
    year = year or date.today().year
    wanted = set(m[:3].title() for m in months)
    for term in student["terms"]:
        if term["year"] == year and set(term["months"]) == wanted:
            return term
    return None

def _find_active_term(student: StudentData) -> Optional[StudentTerm]:
    """The term that contains today's month — used when no specific term is asked for."""
    today_month = date.today().strftime("%b")
    for term in student["terms"]:
        if term["year"] == date.today().year and today_month in term["months"]:
            return term
    return student["terms"][-1] if student["terms"] else None  # fallback: most recent

def get_schedule_for_term(name: str, months: list[str], year: Optional[int] = None) -> str:
    student = load_student(name)
    term = _find_term(student, months, year)
    if term is None:
        available = [f"{t['months'][0]}-{t['months'][-1]} {t['year']}" for t in student["terms"]]
        raise ValueError(f"No {'-'.join(months)} term found for {name}. Available terms: {', '.join(available)}")
    return _render_schedule(name, term)

def get_current_schedule(name: str) -> str:
    student = load_student(name)
    term = _find_active_term(student)
    if term is None:
        raise ValueError(f"No terms found for {name}.")
    return _render_schedule(name, term)

def _render_schedule(name: str, term: StudentTerm) -> str:
    """Same rendering logic as before, just reading from a term dict instead of top-level fields."""
    term_label = f"{term['months'][0]}, {term['months'][1]}, {term['months'][2]}"
    return build_full_schedule(
        name=name,
        day_time=term["day_time"],
        term=term_label,
        year=term["year"],
        absent_list=term.get("absent_dates", []),
        replace_list=term.get("replace_dates", []),
        special_list=term.get("special_slots", [])
    )