"""
Availability is computed here, in Booking Service, even though the raw
working-hours/time-off data lives in Provider Service - that's the
ownership split from the design doc (Provider Service owns the *rules*,
Booking Service owns the *calendar*). We fetch the rules over HTTP and
cross-reference them against our own `Booking` rows so Provider Service
never needs to know a single thing about appointments.
"""
from datetime import datetime, timedelta

import requests
from django.conf import settings

from .models import Booking


def fetch_provider(provider_id):
    url = f"{settings.INTERNAL_SERVICE_URLS['provider']}/internal/providers/{provider_id}"
    response = requests.get(url, timeout=5)
    if response.status_code != 200:
        return None
    return response.json()


def available_slots(provider_id, service_id, date):
    """Returns a list of ISO datetime strings the customer can book on
    `date` (a date object) for `service_id`, given the provider's weekly
    schedule and this service's duration."""
    provider = fetch_provider(provider_id)
    if not provider:
        return []

    service = next((s for s in provider.get("services", []) if s["id"] == str(service_id)), None)
    if not service:
        return []
    duration = timedelta(minutes=service["duration_minutes"])

    weekday = date.weekday()
    schedule = next((wh for wh in provider.get("working_hours", []) if wh["weekday"] == weekday), None)
    if not schedule:
        return []

    day_start = datetime.combine(date, datetime.strptime(schedule["start_time"], "%H:%M:%S").time())
    day_end = datetime.combine(date, datetime.strptime(schedule["end_time"], "%H:%M:%S").time())

    existing = Booking.objects.filter(
        provider_id=provider_id,
        start_time__date=date,
        status__in=["pending_payment", "confirmed"],
    ).values_list("start_time", "end_time")

    slots = []
    cursor = day_start
    while cursor + duration <= day_end:
        slot_end = cursor + duration
        overlaps = any(cursor < existing_end and slot_end > existing_start for existing_start, existing_end in existing)
        if not overlaps:
            slots.append(cursor.isoformat())
        cursor += duration

    return slots
