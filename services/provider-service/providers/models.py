import uuid

from django.db import models


class ProviderProfile(models.Model):
    """Provider Service owns: business profile, verification, portfolio,
    pricing, availability, certificates - everything a customer needs to
    decide whether to book, and everything Booking Service needs to check
    availability against."""

    VERIFICATION_CHOICES = [
        ("unverified", "Unverified"),
        ("pending", "Pending review"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]
    STATUS_CHOICES = [("active", "Active"), ("paused", "Paused"), ("removed", "Removed")]

    user_id = models.UUIDField(primary_key=True)
    business_name = models.CharField(max_length=200)
    email = models.EmailField()
    bio = models.TextField(blank=True, default="")
    category = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default="unverified")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    average_rating = models.FloatField(default=0)
    review_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class VerificationDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=100)
    file_url = models.URLField()
    reviewed = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class PortfolioImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name="portfolio_images")
    url = models.URLField()
    caption = models.CharField(max_length=200, blank=True, default="")
    sort_order = models.IntegerField(default=0)


class Service(models.Model):
    """A single bookable offering, e.g. "Deep house cleaning" at $89, 2h."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(default=60)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WorkingHours(models.Model):
    WEEKDAYS = [(0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday")]

    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name="working_hours")
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ("provider", "weekday")


class TimeOff(models.Model):
    """One-off blocked dates (vacation, holiday) layered on top of the
    recurring WorkingHours schedule."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name="time_off")
    date = models.DateField()
    reason = models.CharField(max_length=200, blank=True, default="")
