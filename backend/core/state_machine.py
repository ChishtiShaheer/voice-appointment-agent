from core import llm_extractor, validators
from integrations import supabase_client, email_client, calendar_client


def _next_missing_field(session: dict, config: dict) -> dict | None:
    for field in config["required_fields"]:
        if field["key"] not in session["collected"]:
            return field
    return None


def _reset_collection(session: dict) -> None:
    session["collected"] = {}
    session["state"] = "COLLECTING"


def handle_message(session: dict, user_text: str, config: dict) -> str:
    state = session["state"]

    if state == "GREETING":
        intent = llm_extractor.detect_intent(user_text)
        if intent == "reschedule_appointment":
            session["pending_intent"] = "reschedule"
            session["state"] = "LOOKUP"
            return "No problem — what phone number is the appointment under?"
        if intent == "cancel_appointment":
            session["pending_intent"] = "cancel"
            session["state"] = "LOOKUP"
            return "Sure — what phone number is the appointment under?"
        _reset_collection(session)
        field = _next_missing_field(session, config)
        return field["prompt"]

    if state == "LOOKUP":
        phone = user_text.strip()
        appointment = supabase_client.find_latest_appointment_by_phone(phone)
        if not appointment:
            return "I couldn't find an appointment under that number. Could you double check it?"
        session["lookup_appointment_id"] = appointment["id"]
        session["lookup_appointment"] = appointment
        if session["pending_intent"] == "cancel":
            session["state"] = "CANCEL_CONFIRMING"
            return (
                f"Found it: {appointment['appointment_type']} on {appointment['appointment_date']} "
                f"at {appointment['appointment_time']}. Cancel this appointment?"
            )
        session["state"] = "COLLECTING"
        session["collected"] = {}
        return "What new date would you like?"

    if state == "CANCEL_CONFIRMING":
        intent = llm_extractor.detect_intent(user_text)
        if intent == "confirm_yes":
            supabase_client.cancel_appointment(session["lookup_appointment_id"])
            session["state"] = "GREETING"
            return "Done — your appointment has been cancelled."
        session["state"] = "GREETING"
        return "Okay, I've left the appointment as is."

    if state == "COLLECTING":
        if session.get("pending_intent") == "reschedule":
            fields = [f for f in config["required_fields"] if f["key"] in ("date", "time")]
        else:
            fields = config["required_fields"]

        current_field = None
        for field in fields:
            if field["key"] not in session["collected"]:
                current_field = field
                break

        if current_field is None:
            session["state"] = "CONFIRMING"
            return _build_confirmation(session, config)

        raw_value = llm_extractor.extract_field(
            current_field["key"], current_field["prompt"], user_text
        )
        if raw_value is None:
            return f"Sorry, I didn't catch that. {current_field['prompt']}"

        ok, normalized = validators.validate_and_normalize(
            current_field["type"], raw_value, config
        )
        if not ok:
            return f"That doesn't look right. {current_field['prompt']}"

        session["collected"][current_field["key"]] = normalized

        next_field = None
        for field in fields:
            if field["key"] not in session["collected"]:
                next_field = field
                break

        if next_field is None:
            session["state"] = "CONFIRMING"
            return _build_confirmation(session, config)

        return next_field["prompt"]

    if state == "CONFIRMING":
        intent = llm_extractor.detect_intent(user_text)
        if intent == "confirm_yes":
            if session.get("pending_intent") == "reschedule":
                supabase_client.reschedule_appointment(
                    session["lookup_appointment_id"], session["collected"]
                )
                session["state"] = "GREETING"
                session["pending_intent"] = None
                return "Your appointment has been rescheduled. See you then!"

            appointment = supabase_client.create_appointment(
                config["business_name"], session["collected"]
            )
            email_client.send_confirmation_email(appointment, config)
            calendar_client.create_calendar_event(appointment, config)
            session["state"] = "GREETING"
            return (
                f"You're all set, {appointment['full_name']}! "
                "A confirmation email is on its way."
            )
        if intent == "confirm_no":
            session["state"] = "GREETING"
            session["collected"] = {}
            return "No problem, cancelled. Let me know if you'd like to start over."
        return "Sorry, could you say yes or no — should I proceed with booking?"

    session["state"] = "GREETING"
    return "Let's start over — how can I help you today?"


def _build_confirmation(session: dict, config: dict) -> str:
    data = dict(session["collected"])
    if "appointment_type" in data:
        for t in config["appointment_types"]:
            if t["id"] == data["appointment_type"]:
                data["appointment_type"] = t["label"]
                break
    if session.get("pending_intent") == "reschedule":
        existing = session.get("lookup_appointment", {})
        return (
            f"Please confirm: move the appointment to "
            f"{data.get('date', existing.get('appointment_date'))} at "
            f"{data.get('time', existing.get('appointment_time'))}. Proceed?"
        )
    return config["confirmation_template"].format(**data)
