from google import genai
from google.genai import types
import json
from config import GEMINI_API_KEY
from prompt import PHOTO_PROMPT, SYSTEM_INSTRUCTION, VOICE_PROMPT
from schedule_logic import build_roster_block

client = genai.Client(api_key=GEMINI_API_KEY)

GEMINI_MODEL = "gemini-3.5-flash-lite"

def get_student_roster() -> None:
    """Get the current student roster or timetable schedule."""
    return None

def add_student_to_student_roster(name: str, start_time: str, end_time: str) -> dict:
    """Add a new student to the roster with their lesson time."""
    return {"name": name, "start_time": start_time, "end_time": end_time}

def get_full_schedule_for_student(name: str) -> dict:
    """Get a student's current 11-lesson schedule, no absences. Use when asked to show/send/provide a schedule."""
    return {"name": name}

def get_schedule_for_term(name: str, months: list[str], year: int = None) -> dict:
    """Get a student's schedule for a specific term/date range, e.g. 'Jan to March' → months=['Jan','Feb','Mar'].
    Use this when a specific date range or term is mentioned. If no year given, assume current year."""
    return {"name": name, "months": months, "year": year}

def report_absence(name: str, absent_date: str) -> dict:
    """Report a student will be absent on a date (dd-mm format), and rebuild their schedule around it."""
    return {"name": name, "absent_date": absent_date}

TOOLS = [get_student_roster, add_student_to_student_roster, get_full_schedule_for_student, report_absence, get_schedule_for_term]

def _route(contents):
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=TOOLS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )
    )
    parts = response.candidates[0].content.parts
    for part in parts:
        if part.function_call:
            return part.function_call.name, dict(part.function_call.args)
    return None, None  # Gemini didn't recognize a matching command

def route_text(text: str):
    return _route(text)


def route_text_with_context(text: str, context: str):
    return _route([context, text])

def route_audio(audio_bytes: bytes):
    return _route([types.Part.from_bytes(data=audio_bytes, mime_type="audio/ogg")])

def extract_from_photo(image_bytes: bytes) -> list:
    prompt = PHOTO_PROMPT.replace("__ROSTER__", build_roster_block())
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type="image/png")
        ]
    )
    return json.loads(response.text.strip().strip("```json").strip("```"))

def extract_from_voice(audio_bytes: bytes) -> dict:
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            VOICE_PROMPT,
            types.Part.from_bytes(data=audio_bytes, mime_type="audio/ogg")
        ]
    )
    return json.loads(response.text.strip().strip("```json").strip("```"))