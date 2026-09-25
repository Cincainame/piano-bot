from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def update_attendance(record_id: int, updates: dict) -> dict | None:
    """Update a row in the attendance table by its id.

    Example:
        update_attendance(12, {"status": "present"})
    """
    response = (
        supabase.table("attendance")
        .insert(updates)
        .execute()
    )
    return response.data[0] if response.data else None


def now() -> str:
    """Return the current date and time in ISO format."""
    from datetime import datetime
    return datetime.now().isoformat()

if __name__ == "__main__":
    # Debug: show what's actually in the table
    rows = supabase.table("student").select("*").limit(5).execute().data
    print(f"Found {len(rows)} row(s):")
    for r in rows:
        print(" ", r)

    # Quick connection test — edit TEST_ID to a real id from the list above
    TEST_ID = 1
    print("\nUpdating attendance...")
    result = update_attendance(
        TEST_ID,
        {"student_id": 1, "term": "Jan, Feb, Mar", "absent_date": "2023-01-01",
         "replacement_date": "", "created_at": now(), "updated_at": now()},
    )
    print("Result:", result)
    if result is None:
        print(f"No row with id={TEST_ID} was updated. Use one of the ids listed above.")

