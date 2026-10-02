import calendar
import json
import logging
from datetime import date
import os
from pathlib import Path
from typing import Optional, TypedDict

LESSONS_PER_TERM = 11

today = date.today()
year = today.year

month_str_to_num = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}


def statusPicker(d: date) -> str:
    return "✅" if d < today else "⭐"

def daytoWeekdayNumber(day: str) -> int:
    return list(calendar.day_name).index(day)

def dateFormatter(raw_date: str) -> date:
    day_str, month_str = raw_date.strip().split("-")
    return date(year, int(month_str), int(day_str))

def find_matching_dates(day_index: int, month_in_nums: list[int], year: int) -> list[tuple[date, str]]:
    matching_dates = []
    for month in month_in_nums:
        for week in calendar.monthcalendar(year, month):
            day = week[day_index]
            if day != 0:
                d = date(year, month, day)
                matching_dates.append((d, statusPicker(d)))
                
    return matching_dates

def compute_past_absences(day: str, months: list[int], year: int, replacement_dates: list[str], absent_dates: list[str]) -> list[str]:
    all_expected = find_matching_dates(daytoWeekdayNumber(day), months, year)
    today = date.today()
    known = set(replacement_dates) | set(absent_dates)
    return [d.strftime("%d-%m") for d, _ in all_expected if d < today and d.strftime("%d-%m") not in known]

def remove_absent_class(matchingDates: list[tuple[date, str]], absentList: list[str]) -> list[tuple[date, str]]:
    for d in absentList:
        date_to_remove = dateFormatter(d)
        matchingDates = [(dd, s) for (dd, s) in matchingDates if dd != date_to_remove]
    return matchingDates

def build_full_schedule(name: str, months: list[int], day: str, time: str,  year: int, replace_list=list[str], absent_list=list[str]) -> str:
    """
    Main entry point. absent_list / replace_list: lists of 'dd-mm' strings.
    special_list: list of (info_string, slot_index) tuples.
    """
    months_str = ", ".join(calendar.month_abbr[m] for m in months)

    dates = find_matching_dates(daytoWeekdayNumber(day), months, year)
    absent_list= compute_past_absences(day, months, year, replace_list, absent_list)
    dates_after_absent = remove_absent_class(dates, absent_list)

    replacedDates = [(dateFormatter(d), statusPicker(dateFormatter(d))) for d in replace_list]
    replaced_date_values = set(d for d, _ in replacedDates)

    all_dates = sorted(dates_after_absent + replacedDates, key=lambda x: x[0])

    lines = [f"{name} Piano Semester ({months_str})", day + time]
    lessonCount = 0
    for d, status in all_dates:
        if lessonCount < LESSONS_PER_TERM:
            lessonCount += 1
            note = " (replacement)" if d in replaced_date_values else ""
            date_str = d if isinstance(d, str) else d.strftime('%d %B')
            lines.append(f"#{lessonCount} - {date_str} {status}{note}")
        else:
            lines.append(f"Backup Date - {d.strftime('%d %B')}")

    replacement = 0
    while lessonCount < LESSONS_PER_TERM:
        replacement += 1
        lessonCount += 1
        lines.append(f"#{lessonCount} - *pending replacement*")

    lines.append("")
    for absent in absent_list:
        lines.append(f"Absent Date - {dateFormatter(absent).strftime('%d %B')} 🔴")
    lines.append("")

    if replacement:
        lines.append(f"Good morning! For {name}'s {months_str} semester, we still have *{replacement}* "
                      f"replacement class to arrange. Let me know when you're free, and we'll find a time that works. 😁")
    else:
        lines.append(f"Good morning! This is {name}'s {months_str} semester schedule. "
                      f"Do let me know if you have any questions. 😁")

    return "\n".join(lines)