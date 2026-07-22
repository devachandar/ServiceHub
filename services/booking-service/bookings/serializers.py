from rest_framework import serializers

from .models import Booking, BookingStatusEvent


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id", "customer_id", "provider_id", "service_id", "service_name", "price",
            "start_time", "end_time", "status", "cancellation_reason", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "customer_id", "provider_id", "created_at", "updated_at"]


class BookingStatusEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingStatusEvent
        fields = ["from_status", "to_status", "note", "created_at"]


class CreateBookingSerializer(serializers.Serializer):
    providerId = serializers.UUIDField()
    serviceId = serializers.UUIDField()
    startTime = serializers.DateTimeField()
