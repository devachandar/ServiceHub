from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Address, CustomerProfile, Preference, SavedProvider
from .permissions import IsAuthenticatedStateless
from .serializers import (
    AddressSerializer,
    CustomerProfileSerializer,
    PreferenceSerializer,
    SavedProviderSerializer,
)


def get_or_create_profile(request):
    profile, _ = CustomerProfile.objects.get_or_create(
        user_id=request.user.id,
        defaults={"email": request.user.email, "full_name": request.user.full_name or ""},
    )
    return profile


class MyProfileView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        profile = get_or_create_profile(request)
        return Response(CustomerProfileSerializer(profile).data)

    def patch(self, request):
        profile = get_or_create_profile(request)
        for field in ["full_name", "phone_number", "avatar_url"]:
            if field in request.data:
                setattr(profile, field, request.data[field])
        profile.save()
        return Response(CustomerProfileSerializer(profile).data)


class InternalProfileDetailView(APIView):
    """Lets other services (e.g. Booking, Review) resolve a display name
    without duplicating profile data."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id):
        try:
            profile = CustomerProfile.objects.get(user_id=user_id)
        except (CustomerProfile.DoesNotExist, ValueError):
            return Response({"error": "Profile not found"}, status=404)
        return Response(CustomerProfileSerializer(profile).data)


class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        profile = get_or_create_profile(request)
        return Response(AddressSerializer(profile.addresses.all(), many=True).data)

    def post(self, request):
        profile = get_or_create_profile(request)
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.data.get("is_default"):
            profile.addresses.update(is_default=False)
        serializer.save(profile=profile)
        return Response(serializer.data, status=201)


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def delete(self, request, address_id):
        deleted, _ = Address.objects.filter(id=address_id, profile__user_id=request.user.id).delete()
        if not deleted:
            return Response({"error": "Address not found"}, status=404)
        return Response(status=204)


class SavedProviderListView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        profile = get_or_create_profile(request)
        return Response(SavedProviderSerializer(profile.saved_providers.all(), many=True).data)

    def post(self, request):
        profile = get_or_create_profile(request)
        provider_id = request.data.get("provider_id")
        if not provider_id:
            return Response({"error": "provider_id is required"}, status=400)
        SavedProvider.objects.get_or_create(profile=profile, provider_id=provider_id)
        return Response(status=201)


class SavedProviderDetailView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def delete(self, request, provider_id):
        SavedProvider.objects.filter(profile__user_id=request.user.id, provider_id=provider_id).delete()
        return Response(status=204)


class PreferenceView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        profile = get_or_create_profile(request)
        prefs, _ = Preference.objects.get_or_create(profile=profile)
        return Response(PreferenceSerializer(prefs).data)

    def patch(self, request):
        profile = get_or_create_profile(request)
        prefs, _ = Preference.objects.get_or_create(profile=profile)
        serializer = PreferenceSerializer(prefs, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
