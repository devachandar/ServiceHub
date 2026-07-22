from rest_framework.response import Response
from rest_framework.views import APIView

from .events import publish_event
from .models import PortfolioImage, ProviderProfile, Service, TimeOff, VerificationDocument, WorkingHours
from .permissions import IsRole
from .serializers import (
    PortfolioImageSerializer,
    ProviderProfileSerializer,
    ProviderSummarySerializer,
    ServiceSerializer,
    VerificationDocumentSerializer,
    WorkingHoursSerializer,
)


def publish_provider_event(name, provider):
    publish_event(name, ProviderProfileSerializer(provider).data)


class OnboardProviderView(APIView):
    """A provider/agent creates (or re-submits) their business profile."""

    permission_classes = [IsRole("provider", "admin")]

    def post(self, request):
        provider, created = ProviderProfile.objects.update_or_create(
            user_id=request.user.id,
            defaults={
                "business_name": request.data.get("businessName", ""),
                "email": request.user.email,
                "bio": request.data.get("bio", ""),
                "category": request.data.get("category", ""),
                "city": request.data.get("city", ""),
                "state": request.data.get("state", ""),
                "latitude": request.data.get("latitude"),
                "longitude": request.data.get("longitude"),
            },
        )
        publish_provider_event("ProviderCreated" if created else "ProviderUpdated", provider)
        return Response(ProviderProfileSerializer(provider).data, status=201 if created else 200)


class MyProviderProfileView(APIView):
    permission_classes = [IsRole("provider", "admin")]

    def get(self, request):
        try:
            provider = ProviderProfile.objects.get(user_id=request.user.id)
        except ProviderProfile.DoesNotExist:
            return Response({"error": "No business profile yet - onboard first"}, status=404)
        return Response(ProviderProfileSerializer(provider).data)

    def patch(self, request):
        try:
            provider = ProviderProfile.objects.get(user_id=request.user.id)
        except ProviderProfile.DoesNotExist:
            return Response({"error": "No business profile yet - onboard first"}, status=404)

        for field in ["business_name", "bio", "category", "city", "state", "latitude", "longitude", "status"]:
            camel = field.split("_")[0] + "".join(w.title() for w in field.split("_")[1:])
            if camel in request.data:
                setattr(provider, field, request.data[camel])
        provider.save()
        publish_provider_event("ProviderUpdated", provider)
        return Response(ProviderProfileSerializer(provider).data)


class ProviderDetailView(APIView):
    """Public detail page - what a customer sees."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, provider_id):
        try:
            provider = ProviderProfile.objects.get(user_id=provider_id, status="active")
        except (ProviderProfile.DoesNotExist, ValueError):
            return Response({"error": "Provider not found"}, status=404)
        return Response(ProviderProfileSerializer(provider).data)


class ProviderListView(APIView):
    """Basic listing, mainly used by Search Service to backfill its index."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        qs = ProviderProfile.objects.filter(status="active").order_by("-created_at")[:200]
        return Response(ProviderProfileSerializer(qs, many=True).data)


class InternalProviderDetailView(APIView):
    """Used by Booking Service to validate a provider/service before
    creating an appointment, and by Review Service to update rating stats."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, provider_id):
        try:
            provider = ProviderProfile.objects.get(user_id=provider_id)
        except (ProviderProfile.DoesNotExist, ValueError):
            return Response({"error": "Provider not found"}, status=404)
        return Response(ProviderProfileSerializer(provider).data)


class InternalRatingUpdateView(APIView):
    """Review Service calls this after a new review to keep the
    denormalized average_rating / review_count in sync."""

    authentication_classes = []
    permission_classes = []

    def post(self, request, provider_id):
        try:
            provider = ProviderProfile.objects.get(user_id=provider_id)
        except (ProviderProfile.DoesNotExist, ValueError):
            return Response({"error": "Provider not found"}, status=404)
        provider.average_rating = request.data.get("averageRating", provider.average_rating)
        provider.review_count = request.data.get("reviewCount", provider.review_count)
        provider.save(update_fields=["average_rating", "review_count", "updated_at"])
        publish_provider_event("ProviderUpdated", provider)
        return Response(status=204)


# ---------- Services offered ----------
class ServiceListCreateView(APIView):
    permission_classes = [IsRole("provider", "admin")]

    def get(self, request):
        provider = ProviderProfile.objects.get(user_id=request.user.id)
        return Response(ServiceSerializer(provider.services.all(), many=True).data)

    def post(self, request):
        provider = ProviderProfile.objects.get(user_id=request.user.id)
        serializer = ServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(provider=provider)
        publish_provider_event("ProviderUpdated", provider)
        return Response(serializer.data, status=201)


class ServiceDetailView(APIView):
    permission_classes = [IsRole("provider", "admin")]

    def patch(self, request, service_id):
        try:
            service = Service.objects.get(id=service_id, provider__user_id=request.user.id)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=404)
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        publish_provider_event("ProviderUpdated", service.provider)
        return Response(serializer.data)

    def delete(self, request, service_id):
        deleted, _ = Service.objects.filter(id=service_id, provider__user_id=request.user.id).delete()
        if not deleted:
            return Response({"error": "Service not found"}, status=404)
        return Response(status=204)


# ---------- Working hours ----------
class WorkingHoursView(APIView):
    permission_classes = [IsRole("provider", "admin")]

    def get(self, request):
        provider = ProviderProfile.objects.get(user_id=request.user.id)
        return Response(WorkingHoursSerializer(provider.working_hours.order_by("weekday"), many=True).data)

    def put(self, request):
        """Replace the whole weekly schedule in one call:
        [{"weekday": 0, "startTime": "09:00", "endTime": "17:00"}, ...]"""
        provider = ProviderProfile.objects.get(user_id=request.user.id)
        provider.working_hours.all().delete()
        for entry in request.data:
            WorkingHours.objects.create(
                provider=provider,
                weekday=entry["weekday"],
                start_time=entry["startTime"],
                end_time=entry["endTime"],
            )
        return Response(WorkingHoursSerializer(provider.working_hours.order_by("weekday"), many=True).data)


class TimeOffView(APIView):
    permission_classes = [IsRole("provider", "admin")]

    def post(self, request):
        provider = ProviderProfile.objects.get(user_id=request.user.id)
        TimeOff.objects.create(provider=provider, date=request.data["date"], reason=request.data.get("reason", ""))
        return Response(status=201)


# ---------- Portfolio & verification ----------
class PortfolioView(APIView):
    permission_classes = [IsRole("provider", "admin")]

    def post(self, request):
        provider = ProviderProfile.objects.get(user_id=request.user.id)
        urls = request.data.get("urls", [])
        for i, url in enumerate(urls):
            PortfolioImage.objects.create(provider=provider, url=url, sort_order=i)
        return Response(PortfolioImageSerializer(provider.portfolio_images.all(), many=True).data, status=201)


class VerificationDocumentView(APIView):
    permission_classes = [IsRole("provider", "admin")]

    def post(self, request):
        provider = ProviderProfile.objects.get(user_id=request.user.id)
        doc = VerificationDocument.objects.create(
            provider=provider,
            document_type=request.data.get("documentType", "other"),
            file_url=request.data["fileUrl"],
        )
        provider.verification_status = "pending"
        provider.save(update_fields=["verification_status", "updated_at"])
        return Response(VerificationDocumentSerializer(doc).data, status=201)


# ---------- Admin ----------
class AdminProviderListView(APIView):
    permission_classes = [IsRole("admin")]

    def get(self, request):
        qs = ProviderProfile.objects.all().order_by("-created_at")
        status_filter = request.query_params.get("verificationStatus")
        if status_filter:
            qs = qs.filter(verification_status=status_filter)
        return Response(ProviderProfileSerializer(qs[:200], many=True).data)


class AdminVerifyProviderView(APIView):
    permission_classes = [IsRole("admin")]

    def patch(self, request, provider_id):
        decision = request.data.get("decision")
        if decision not in ("verified", "rejected"):
            return Response({"error": "decision must be 'verified' or 'rejected'"}, status=400)
        try:
            provider = ProviderProfile.objects.get(user_id=provider_id)
        except (ProviderProfile.DoesNotExist, ValueError):
            return Response({"error": "Provider not found"}, status=404)
        provider.verification_status = decision
        provider.save(update_fields=["verification_status", "updated_at"])
        publish_provider_event("ProviderVerified", provider)
        return Response(ProviderProfileSerializer(provider).data)
