import uuid

from django.db import models


class CustomerProfile(models.Model):
    """User Service owns everything about a customer EXCEPT their
    credentials (that's Auth Service). user_id is the JWT subject - there is
    no foreign key to a local users table because there isn't one."""

    user_id = models.UUIDField(primary_key=True)
    email = models.EmailField()
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=32, blank=True, default="")
    avatar_url = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=50, default="Home")
    line1 = models.CharField(max_length=200)
    line2 = models.CharField(max_length=200, blank=True, default="")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class SavedProvider(models.Model):
    profile = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="saved_providers")
    provider_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("profile", "provider_id")


class Preference(models.Model):
    profile = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE, related_name="preferences")
    preferred_categories = models.JSONField(default=list, blank=True)
    notify_email = models.BooleanField(default=True)
    notify_sms = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
