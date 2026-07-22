import re
from datetime import datetime, date
from dateutil import parser as dateparser


def validate_and_normalize(field_type: str, value: str, config: dict) -> tuple[bool, str]:
    if value is None or not str(value).strip():
        return False, ""

    value = str(value).strip()

    if field_type == "text":
        return True, value

    if field_type == "phone":
        digits = re.sub(r"[^\d+]", "", value)
        if len(re.sub(r"\D", "", digits)) < 7:
            return False, ""
        return True, digits

    if field_type == "date":
        try:
            parsed = dateparser.parse(value, fuzzy=True, default=datetime.now())
            if parsed.date() < date.today():
                return False, ""
            return True, parsed.strftime("%Y-%m-%d")
        except (ValueError, OverflowError):
            return False, ""

    if field_type == "time":
        try:
            parsed = dateparser.parse(value, fuzzy=True, default=datetime.now())
            hhmm = parsed.strftime("%H:%M")
            start = config.get("working_hours", {}).get("start", "00:00")
            end = config.get("working_hours", {}).get("end", "23:59")
            if not (start <= hhmm <= end):
                return False, ""
            return True, hhmm
        except (ValueError, OverflowError):
            return False, ""

    if field_type == "enum":
        options = [t["id"] for t in config.get("appointment_types", [])]
        labels = {t["label"].lower(): t["id"] for t in config.get("appointment_types", [])}
        lowered = value.lower()
        if lowered in options:
            return True, lowered
        if lowered in labels:
            return True, labels[lowered]
        for label, opt_id in labels.items():
            if label in lowered or lowered in label:
                return True, opt_id
        return False, ""

    return True, value
