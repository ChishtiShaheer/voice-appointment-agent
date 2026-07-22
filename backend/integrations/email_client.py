import os
import resend

resend.api_key = os.environ.get("RESEND_API_KEY", "")
FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "onboarding@resend.dev")


def send_confirmation_email(appointment: dict, config: dict) -> None:
    if not resend.api_key:
        return
    to_email = appointment.get("email")
    if not to_email:
        return
    resend.Emails.send({
        "from": FROM_EMAIL,
        "to": to_email,
        "subject": f"Appointment confirmed - {config['business_name']}",
        "html": (
            f"<p>Hi {appointment['full_name']},</p>"
            f"<p>Your {appointment['appointment_type']} appointment on "
            f"{appointment['appointment_date']} at {appointment['appointment_time']} "
            f"is confirmed.</p>"
            f"<p>{config['business_name']}</p>"
        ),
    })
