from google import genai
from google.genai import types, errors
import json
from config import GEMINI_API_KEY
from prompt import PHOTO_PROMPT, SYSTEM_INSTRUCTION, VOICE_PROMPT
from schedule_logic import build_roster_block, parse_roster

client = genai.Client(api_key=GEMINI_API_KEY)

GEMINI_MODEL = "gemini-3.6-flash"

# The tool `name` strings below are dispatched in bot/main.py (e.g.
# "get_student_roster", "add_student_to_student_roster"). Keep them in sync
# with the handlers there. The schema is built explicitly here — instead of
# deriving it from Python function stubs — so `name` can be enum-constrained
# to the live roster and the model can't hallucinate names like Jaryl->Jayden.


def _build_tools() -> types.Tool:
    """Build the function-calling schema, constraining `name` to the current
    roster via an enum.

    Rebuilt per request, so edits to data/student_roster.json take effect
    without a restart. If the roster can't be loaded (or is empty), `name`
    falls back to an unconstrained string so routing still works.

    add_student_to_student_roster deliberately keeps `name` as a free string —
    its purpose is to add a NEW student, so it must not be locked to names
    that already exist.
    """
    try:
        names = list(parse_roster().keys())
    except Exception:
        names = []

    # An empty enum would be rejected by the API; fall back to a plain string.
    name_schema = (
        types.Schema(type="STRING", enum=names) if names else types.Schema(type="STRING")
    )
    str_schema = types.Schema(type="STRING")

    absence_item = types.Schema(
        type="OBJECT",
        properties={"name": name_schema, "absent_date": str_schema},
        required=["name", "absent_date"],
    )

    return types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="get_student_roster",
            description="Get the current student roster or timetable schedule.",
            parameters=types.Schema(type="OBJECT", properties={}),
        ),
        types.FunctionDeclaration(
            name="add_student_to_student_roster",
            description="Add a new student to the roster with their lesson time.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "name": str_schema,
                    "start_time": str_schema,
                    "end_time": str_schema,
                },
                required=["name", "start_time", "end_time"],
            ),
        ),
        types.FunctionDeclaration(
            name="get_full_schedule_for_student",
            description="Get a student's current 11-lesson schedule, no absences. Use when asked to show/send/provide a schedule.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"name": name_schema},
                required=["name"],
            ),
        ),
        types.FunctionDeclaration(
            name="get_schedule_for_term",
            description="Get a student's schedule for a specific term/date range, e.g. 'Jan to March' -> months=['Jan','Feb','Mar']. Use this when a specific date range or term is mentioned. If no year given, assume current year.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "name": name_schema,
                    "months": types.Schema(type="ARRAY", items=str_schema),
                    "year": types.Schema(type="INTEGER"),
                },
                required=["name", "months"],
            ),
        ),
        types.FunctionDeclaration(
            name="report_absence",
            description="Report that one or more students will be absent on a date (dd-mm format), and rebuild their schedule around it.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"absences": types.Schema(type="ARRAY", items=absence_item)},
                required=["absences"],
            ),
        ),
    ])


def _route(contents):
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[_build_tools()],
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
    try:
        return _route([types.Part.from_bytes(data=audio_bytes, mime_type="audio/ogg")])
    except errors.APIError as e:
        print(f"API error routing audio: {e}")
        return None, None
    except Exception as e:
        print(f"Error routing audio: {e}")
        return None, None

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
