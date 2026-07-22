import uuid

from django.db import models


class Invoice(models.Model):
    """Payment Service owns: invoices, transactions, refunds, payouts.
    Created automatically when Booking Service publishes BookingCreated,
    via the `listen_events` -> Celery task path (see events_handlers.py /
    tasks.py) so a broker hiccup gets retried instead of silently losing
    the invoice."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
        ("partially_refunded", "Partially refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_id = models.UUIDField(unique=True)
    customer_id = models.UUIDField()
    provider_id = models.UUIDField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    TYPE_CHOICES = [("charge", "Charge"), ("refund", "Refund"), ("payout", "Payout")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    provider_reference = models.CharField(max_length=100, blank=True, default="")
    succeeded = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Payout(models.Model):
    """Periodic aggregate payout to a provider (Celery beat could schedule
    this weekly in a real deployment)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider_id = models.UUIDField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(max_length=20, default="scheduled")
    created_at = models.DateTimeField(auto_now_add=True)
