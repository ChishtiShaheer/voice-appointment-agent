import os
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
TOKEN_PATH = os.environ.get("GOOGLE_TOKEN_PATH", "google_token.json")


def _get_service():
    if not os.path.exists(TOKEN_PATH):
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    return build("calendar", "v3", credentials=creds)


def create_calendar_event(appointment: dict, config: dict) -> str | None:
    service = _get_service()
    if service is None:
        return None

    date_str = appointment["appointment_date"]
    time_str = appointment["appointment_time"]
    start_dt = datetime.datetime.fromisoformat(f"{date_str}T{time_str}:00")
    duration = 30
    for t in config["appointment_types"]:
        if t["label"] == appointment["appointment_type"] or t["id"] == appointment["appointment_type"]:
            duration = t["duration_minutes"]
            break
    end_dt = start_dt + datetime.timedelta(minutes=duration)

    event = {
        "summary": f"{appointment['appointment_type']} - {appointment['full_name']}",
        "description": appointment.get("reason", ""),
        "start": {"dateTime": start_dt.isoformat(), "timeZone": config["timezone"]},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": config["timezone"]},
    }
    created = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return created.get("id")
