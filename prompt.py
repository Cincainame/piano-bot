PHOTO_PROMPT = """
This is a piano attendance sheet. It may contain multiple students' information.

Known class roster (use to confirm each day_time):
__ROSTER__


For EVERY student visible on the sheet, return a JSON array, no markdown:
[
{{
  "name": "{name}",
  "day_time": "e.g. Sunday 12pm-130pm",
  "months": ["Jul", "Aug", "Sep"],
  "year": 2026,
  "attended_dates": ["04-07", "12-07", ...],
  "replacement_dates": ["20-07", ...],
  "absent_dates": [],
  "specified_absent_dates": [],
  "unclear_dates": []
}},
...
]

Dates in dd-mm format. "R" marks mean a replacement/make-up class happened —
put those in replacement_dates. Everything else written is an attended date.
Only extract what's visibly marked — do not infer or calculate absences.
If a specific date's mark is illegible, list it in that student's unclear_dates
instead of guessing. If a name is written but doesn't clearly match the known
roster, still include it as written — do not silently correct or drop it.
"""

VOICE_PROMPT = """
Return what I've said
"""