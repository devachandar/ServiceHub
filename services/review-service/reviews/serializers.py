from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id", "booking_id", "customer_id", "provider_id", "rating",
            "comment", "provider_response", "flagged", "hidden", "created_at",
        ]
        read_only_fields = ["id", "customer_id", "provider_id", "flagged", "hidden", "created_at"]


class CreateReviewSerializer(serializers.Serializer):
    bookingId = serializers.UUIDField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, default="")
