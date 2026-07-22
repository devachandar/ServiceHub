from rest_framework import serializers

from .models import PortfolioImage, ProviderProfile, Service, TimeOff, VerificationDocument, WorkingHours


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "name", "description", "price", "duration_minutes", "active", "created_at"]
        read_only_fields = ["id", "created_at"]


class WorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = ["weekday", "start_time", "end_time"]


class PortfolioImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioImage
        fields = ["id", "url", "caption", "sort_order"]
        read_only_fields = ["id"]


class VerificationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationDocument
        fields = ["id", "document_type", "file_url", "reviewed", "uploaded_at"]
        read_only_fields = ["id", "reviewed", "uploaded_at"]


class ProviderProfileSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    working_hours = WorkingHoursSerializer(many=True, read_only=True)
    portfolio_images = PortfolioImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProviderProfile
        fields = [
            "user_id", "business_name", "email", "bio", "category", "city", "state",
            "latitude", "longitude", "verification_status", "status",
            "average_rating", "review_count", "services", "working_hours",
            "portfolio_images", "created_at", "updated_at",
        ]
        read_only_fields = [
            "user_id", "verification_status", "average_rating", "review_count",
            "created_at", "updated_at",
        ]


class ProviderSummarySerializer(serializers.ModelSerializer):
    """Lighter payload used for internal service-to-service lookups
    (Booking Service resolving a provider before creating an appointment)."""

    class Meta:
        model = ProviderProfile
        fields = ["user_id", "business_name", "category", "city", "state", "status", "verification_status"]
