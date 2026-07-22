import uuid

from django.db import models


class Booking(models.Model):
    """Booking Service owns: appointments, calendar, status, cancellation,
    reschedule. It does NOT own provider availability rules (Provider
    Service does) or payment (Payment Service does) - it just records that
    a slot was claimed and publishes events for the rest of the system."""

    STATUS_CHOICES = [
        ("pending_payment", "Pending payment"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("rescheduled", "Rescheduled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.UUIDField()
    provider_id = models.UUIDField()
    service_id = models.UUIDField()
    service_name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending_payment")
    cancellation_reason = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["provider_id", "start_time"]),
            models.Index(fields=["customer_id"]),
        ]


class BookingStatusEvent(models.Model):
    """Append-only history of status transitions, useful for disputes and
    for the provider/customer activity timeline."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="status_events")
    from_status = models.CharField(max_length=20)
    to_status = models.CharField(max_length=20)
    note = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
