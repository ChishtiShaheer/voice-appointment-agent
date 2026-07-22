import json
import os
from groq import Groq

_client = None
MODEL = "llama-3.3-70b-versatile"


def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    return _client


def detect_intent(user_text: str) -> str:
    system = (
        "Classify the user's message into exactly one of: "
        "book_appointment, reschedule_appointment, cancel_appointment, "
        "confirm_yes, confirm_no, other. "
        'Respond with ONLY a JSON object like {"intent": "book_appointment"}.'
    )
    resp = get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_text},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    try:
        return json.loads(resp.choices[0].message.content)["intent"]
    except (json.JSONDecodeError, KeyError):
        return "other"


def extract_field(field_key: str, field_prompt: str, user_text: str) -> str | None:
    system = (
        f"The assistant asked: \"{field_prompt}\". "
        f"Extract the value of \"{field_key}\" from the user's reply. "
        'Respond with ONLY a JSON object like {"value": "..."}. '
        'If no usable value is present, use {"value": null}.'
    )
    resp = get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_text},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    try:
        return json.loads(resp.choices[0].message.content)["value"]
    except (json.JSONDecodeError, KeyError):
        return None
