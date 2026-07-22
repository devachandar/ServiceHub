import requests
from django.conf import settings

from .tasks import send_email_task


def _resolve_user_email(user_id):
    try:
        res = requests.get(f"{settings.INTERNAL_SERVICE_URLS['auth']}/internal/users/{user_id}", timeout=5)
        if res.status_code == 200:
            return res.json().get("email")
    except requests.RequestException:
        pass
    return None


def _resolve_provider_email(provider_id):
    try:
        res = requests.get(f"{settings.INTERNAL_SERVICE_URLS['provider']}/internal/providers/{provider_id}", timeout=5)
        if res.status_code == 200:
            return res.json().get("email")
    except requests.RequestException:
        pass
    return None


def handle_user_registered(payload):
    send_email_task.delay("welcome", payload["email"], {"fullName": payload["fullName"]})


def handle_booking_created(payload):
    customer_email = _resolve_user_email(payload["customerId"])
    provider_email = _resolve_provider_email(payload["providerId"])
    ctx = {
        "providerName": payload.get("providerName", "your provider"),
        "serviceName": payload["service_name"],
        "startTime": payload["start_time"],
    }
    if customer_email:
        send_email_task.delay("booking_confirmation", customer_email, ctx)
    if provider_email:
        send_email_task.delay("new_booking_for_provider", provider_email, ctx)


def handle_payment_captured(payload):
    customer_email = _resolve_user_email(payload["customerId"])
    if customer_email:
        send_email_task.delay("payment_receipt", customer_email, {"amount": payload["amount"]})


def handle_review_created(payload):
    provider_email = _resolve_provider_email(payload["provider_id"])
    if provider_email:
        send_email_task.delay("new_review", provider_email, {"rating": payload["rating"]})


HANDLERS = {
    "UserRegistered": handle_user_registered,
    "BookingCreated": handle_booking_created,
    "PaymentCaptured": handle_payment_captured,
    "ReviewCreated": handle_review_created,
}
