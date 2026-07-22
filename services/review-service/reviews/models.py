import uuid

from django.db import models


class Review(models.Model):
    """Review Service owns: ratings, comments, average rating computation.
    One review per completed booking - enforced at the application layer by
    checking Booking Service before allowing a review to be created."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_id = models.UUIDField(unique=True)
    customer_id = models.UUIDField()
    provider_id = models.UUIDField()
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, default="")
    provider_response = models.TextField(blank=True, default="")
    flagged = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["provider_id"])]
