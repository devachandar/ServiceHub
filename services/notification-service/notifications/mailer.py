import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

TEMPLATES = {
    "welcome": lambda ctx: (
        "Welcome to ServiceHub",
        f"Hi {ctx['fullName']}, welcome to ServiceHub! Start browsing providers or finish your business profile.",
    ),
    "booking_confirmation": lambda ctx: (
        f"Booking confirmed with {ctx['providerName']}",
        f"Your booking for {ctx['serviceName']} on {ctx['startTime']} is confirmed.",
    ),
    "new_booking_for_provider": lambda ctx: (
        "You have a new booking",
        f"A customer just booked {ctx['serviceName']} for {ctx['startTime']}. Check your dashboard for details.",
    ),
    "payment_receipt": lambda ctx: (
        "Payment received",
        f"We've received your payment of ${ctx['amount']} for your recent booking.",
    ),
    "new_review": lambda ctx: (
        "You have a new review",
        f"A customer left you a {ctx['rating']}-star review. Log in to respond.",
    ),
}


def send(template_name, to_email, context):
    if not to_email:
        return {"delivered": False, "reason": "no recipient email"}

    build = TEMPLATES.get(template_name)
    if not build:
        raise ValueError(f"Unknown notification template: {template_name}")
    subject, body = build(context)

    if not settings.EMAIL_BACKEND_CONFIGURED:
        logger.info("(console fallback) -> %s | Subject: %s | %s", to_email, subject, body)
        return {"delivered": False, "reason": "SMTP not configured, logged only"}

    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
    return {"delivered": True}
