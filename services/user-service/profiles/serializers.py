from rest_framework import serializers

from .models import Address, CustomerProfile, Preference, SavedProvider


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "label", "line1", "line2", "city", "state", "postal_code", "is_default", "created_at"]
        read_only_fields = ["id", "created_at"]


class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = ["preferred_categories", "notify_email", "notify_sms", "updated_at"]
        read_only_fields = ["updated_at"]


class CustomerProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    preferences = PreferenceSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            "user_id", "email", "full_name", "phone_number", "avatar_url",
            "addresses", "preferences", "created_at", "updated_at",
        ]
        read_only_fields = ["user_id", "email", "created_at", "updated_at"]


class SavedProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedProvider
        fields = ["provider_id", "created_at"]
        read_only_fields = ["created_at"]
