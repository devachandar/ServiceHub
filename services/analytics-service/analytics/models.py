from django.db import models


class DailyMetric(models.Model):
    """One row per calendar day - incremented as events arrive. Simple by
    design: a real Analytics Service would likely use a time-series store,
    but this keeps the KPI dashboard demoable with plain Postgres."""

    date = models.DateField(unique=True)
    bookings_created = models.IntegerField(default=0)
    bookings_completed = models.IntegerField(default=0)
    bookings_cancelled = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    new_reviews = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)


class ProviderMetric(models.Model):
    provider_id = models.UUIDField(unique=True)
    total_bookings = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
