from decimal import Decimal

from django.utils import timezone

from .models import DailyMetric, ProviderMetric


def _today():
    metric, _ = DailyMetric.objects.get_or_create(date=timezone.now().date())
    return metric


def handle_user_registered(payload):
    metric = _today()
    metric.new_users += 1
    metric.save(update_fields=["new_users"])


def handle_booking_created(payload):
    metric = _today()
    metric.bookings_created += 1
    metric.save(update_fields=["bookings_created"])

    provider_metric, _ = ProviderMetric.objects.get_or_create(provider_id=payload["providerId"])
    provider_metric.total_bookings += 1
    provider_metric.save(update_fields=["total_bookings"])


def handle_booking_completed(payload):
    metric = _today()
    metric.bookings_completed += 1
    metric.save(update_fields=["bookings_completed"])


def handle_booking_cancelled(payload):
    metric = _today()
    metric.bookings_cancelled += 1
    metric.save(update_fields=["bookings_cancelled"])


def handle_payment_captured(payload):
    metric = _today()
    metric.revenue += Decimal(str(payload["amount"]))
    metric.save(update_fields=["revenue"])

    provider_metric, _ = ProviderMetric.objects.get_or_create(provider_id=payload["providerId"])
    provider_metric.total_revenue += Decimal(str(payload["amount"]))
    provider_metric.save(update_fields=["total_revenue"])


def handle_review_created(payload):
    metric = _today()
    metric.new_reviews += 1
    metric.save(update_fields=["new_reviews"])

    provider_metric, _ = ProviderMetric.objects.get_or_create(provider_id=payload["provider_id"])
    provider_metric.total_reviews += 1
    provider_metric.save(update_fields=["total_reviews"])


HANDLERS = {
    "UserRegistered": handle_user_registered,
    "BookingCreated": handle_booking_created,
    "BookingCompleted": handle_booking_completed,
    "BookingCancelled": handle_booking_cancelled,
    "PaymentCaptured": handle_payment_captured,
    "ReviewCreated": handle_review_created,
}
