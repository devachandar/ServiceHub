import requests
from django.conf import settings
from django.db.models import Avg, Count
from rest_framework.response import Response
from rest_framework.views import APIView

from .events import publish_event
from .models import Review
from .permissions import IsAuthenticatedStateless, IsRole
from .serializers import CreateReviewSerializer, ReviewSerializer


def sync_provider_rating(provider_id):
    stats = Review.objects.filter(provider_id=provider_id, hidden=False).aggregate(avg=Avg("rating"), count=Count("id"))
    url = f"{settings.INTERNAL_SERVICE_URLS['provider']}/internal/providers/{provider_id}/rating"
    try:
        requests.post(url, json={"averageRating": round(stats["avg"] or 0, 2), "reviewCount": stats["count"]}, timeout=5)
    except requests.RequestException:
        pass


class CreateReviewView(APIView):
    permission_classes = [IsRole("customer", "admin")]

    def post(self, request):
        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if Review.objects.filter(booking_id=data["bookingId"]).exists():
            return Response({"error": "This booking has already been reviewed"}, status=409)

        booking_url = f"{settings.INTERNAL_SERVICE_URLS['booking']}/internal/bookings/{data['bookingId']}"
        try:
            booking_res = requests.get(booking_url, timeout=5)
        except requests.RequestException:
            return Response({"error": "Could not verify this booking right now"}, status=503)
        if booking_res.status_code != 200:
            return Response({"error": "Booking not found"}, status=404)
        booking = booking_res.json()

        if str(booking["customer_id"]) != str(request.user.id):
            return Response({"error": "You can only review your own bookings"}, status=403)
        if booking["status"] != "completed":
            return Response({"error": "You can only review a completed booking"}, status=400)

        review = Review.objects.create(
            booking_id=data["bookingId"],
            customer_id=request.user.id,
            provider_id=booking["provider_id"],
            rating=data["rating"],
            comment=data.get("comment", ""),
        )
        sync_provider_rating(review.provider_id)
        publish_event("ReviewCreated", ReviewSerializer(review).data)
        return Response(ReviewSerializer(review).data, status=201)


class ProviderReviewsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, provider_id):
        qs = Review.objects.filter(provider_id=provider_id, hidden=False).order_by("-created_at")
        return Response(ReviewSerializer(qs, many=True).data)


class MyReviewsView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        qs = Review.objects.filter(customer_id=request.user.id).order_by("-created_at")
        return Response(ReviewSerializer(qs, many=True).data)


class RespondToReviewView(APIView):
    permission_classes = [IsRole("provider", "admin")]

    def post(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id, provider_id=request.user.id)
        except (Review.DoesNotExist, ValueError):
            return Response({"error": "Review not found"}, status=404)
        review.provider_response = request.data.get("response", "")
        review.save(update_fields=["provider_response"])
        return Response(ReviewSerializer(review).data)


class AdminModerateReviewView(APIView):
    """Admin can hide (soft-remove) or flag a review - Step 2 'Moderate reviews'."""

    permission_classes = [IsRole("admin")]

    def patch(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id)
        except (Review.DoesNotExist, ValueError):
            return Response({"error": "Review not found"}, status=404)
        if "hidden" in request.data:
            review.hidden = bool(request.data["hidden"])
        if "flagged" in request.data:
            review.flagged = bool(request.data["flagged"])
        review.save(update_fields=["hidden", "flagged"])
        sync_provider_rating(review.provider_id)
        return Response(ReviewSerializer(review).data)
