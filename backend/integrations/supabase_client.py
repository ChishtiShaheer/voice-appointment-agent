import os
from supabase import create_client, Client

_client: Client = create_client(
    os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"]
)
TABLE = "appointments"


def create_appointment(business_name: str, collected: dict) -> dict:
    row = {
        "business_name": business_name,
        "full_name": collected["full_name"],
        "phone_number": collected["phone_number"],
        "email": collected.get("email"),
        "appointment_type": collected["appointment_type"],
        "appointment_date": collected["date"],
        "appointment_time": collected["time"],
        "reason": collected.get("reason", ""),
        "status": "booked",
    }
    result = _client.table(TABLE).insert(row).execute()
    return result.data[0]

def find_latest_appointment_by_phone(phone_number: str) -> dict | None:
    result = (
        _client.table(TABLE)
        .select("*")
        .eq("phone_number", phone_number)
        .eq("status", "booked")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def reschedule_appointment(appointment_id: str, collected: dict) -> dict:
    updates = {"status": "rescheduled"}
    if "date" in collected:
        updates["appointment_date"] = collected["date"]
    if "time" in collected:
        updates["appointment_time"] = collected["time"]
    result = (
        _client.table(TABLE).update(updates).eq("id", appointment_id).execute()
    )
    return result.data[0]


def cancel_appointment(appointment_id: str) -> None:
    _client.table(TABLE).update({"status": "cancelled"}).eq(
        "id", appointment_id
    ).execute()


def list_appointments() -> list[dict]:
    result = (
        _client.table(TABLE).select("*").order("created_at", desc=True).execute()
    )
    return result.data
