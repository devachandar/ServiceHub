from datetime import datetime, timedelta

from django.utils.dateparse import parse_date
from rest_framework.response import Response
from rest_framework.views import APIView

from .availability import available_slots, fetch_provider
from .events import publish_event
from .models import Booking, BookingStatusEvent
from .permissions import IsAuthenticatedStateless, IsRole
from .serializers import BookingSerializer, CreateBookingSerializer


class AvailabilityView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, provider_id):
        service_id = request.query_params.get("serviceId")
        date_str = request.query_params.get("date")
        if not service_id or not date_str:
            return Response({"error": "serviceId and date query params are required"}, status=400)
        date = parse_date(date_str)
        if not date:
            return Response({"error": "date must be YYYY-MM-DD"}, status=400)
        return Response({"slots": available_slots(provider_id, service_id, date)})


class CreateBookingView(APIView):
    permission_classes = [IsRole("customer", "admin")]

    def post(self, request):
        serializer = CreateBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        provider = fetch_provider(data["providerId"])
        if not provider or provider.get("verification_status") != "verified":
            return Response({"error": "This provider isn't bookable right now"}, status=400)

        service = next((s for s in provider["services"] if s["id"] == str(data["serviceId"])), None)
        if not service or not service["active"]:
            return Response({"error": "That service is no longer offered"}, status=400)

        start_time = data["startTime"]
        end_time = start_time + timedelta(minutes=service["duration_minutes"])

        overlap = Booking.objects.filter(
            provider_id=data["providerId"],
            status__in=["pending_payment", "confirmed"],
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()
        if overlap:
            return Response({"error": "That time slot was just taken - pick another"}, status=409)

        booking = Booking.objects.create(
            customer_id=request.user.id,
            provider_id=data["providerId"],
            service_id=data["serviceId"],
            service_name=service["name"],
            price=service["price"],
            start_time=start_time,
            end_time=end_time,
        )
        BookingStatusEvent.objects.create(booking=booking, from_status="", to_status="pending_payment")

        publish_event(
            "BookingCreated",
            {
                **BookingSerializer(booking).data,
                "customerId": str(booking.customer_id),
                "providerId": str(booking.provider_id),
                "providerName": provider["business_name"],
            },
        )
        return Response(BookingSerializer(booking).data, status=201)


class MyBookingsView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        qs = Booking.objects.filter(customer_id=request.user.id).order_by("-start_time")
        return Response(BookingSerializer(qs, many=True).data)


class ProviderBookingsView(APIView):
    permission_classes = [IsRole("provider", "admin")]

    def get(self, request):
        qs = Booking.objects.filter(provider_id=request.user.id).order_by("-start_time")
        return Response(BookingSerializer(qs, many=True).data)


def _transition(booking, new_status, note=""):
    old_status = booking.status
    booking.status = new_status
    booking.save(update_fields=["status", "updated_at"])
    BookingStatusEvent.objects.create(booking=booking, from_status=old_status, to_status=new_status, note=note)


class CancelBookingView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def patch(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except (Booking.DoesNotExist, ValueError):
            return Response({"error": "Booking not found"}, status=404)

        is_owner = str(booking.customer_id) == str(request.user.id) or str(booking.provider_id) == str(request.user.id)
        if not is_owner and request.user.role != "admin":
            return Response({"error": "You cannot modify this booking"}, status=403)
        if booking.status in ("completed", "cancelled"):
            return Response({"error": f"Booking is already {booking.status}"}, status=400)

        reason = request.data.get("reason", "")
        booking.cancellation_reason = reason
        _transition(booking, "cancelled", note=reason)

        publish_event(
            "BookingCancelled",
            {**BookingSerializer(booking).data, "customerId": str(booking.customer_id), "providerId": str(booking.provider_id)},
        )
        return Response(BookingSerializer(booking).data)


class RescheduleBookingView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def patch(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except (Booking.DoesNotExist, ValueError):
            return Response({"error": "Booking not found"}, status=404)

        if str(booking.customer_id) != str(request.user.id) and request.user.role != "admin":
            return Response({"error": "Only the customer can reschedule this booking"}, status=403)

        new_start = request.data.get("startTime")
        if not new_start:
            return Response({"error": "startTime is required"}, status=400)
        new_start = datetime.fromisoformat(new_start)
        duration = booking.end_time - booking.start_time
        new_end = new_start + duration

        overlap = (
            Booking.objects.filter(
                provider_id=booking.provider_id,
                status__in=["pending_payment", "confirmed"],
                start_time__lt=new_end,
                end_time__gt=new_start,
            )
            .exclude(id=booking.id)
            .exists()
        )
        if overlap:
            return Response({"error": "That time slot isn't available"}, status=409)

        booking.start_time, booking.end_time = new_start, new_end
        _transition(booking, "confirmed" if booking.status == "confirmed" else booking.status, note="Rescheduled")
        booking.save(update_fields=["start_time", "end_time", "updated_at"])

        publish_event("BookingRescheduled", BookingSerializer(booking).data)
        return Response(BookingSerializer(booking).data)


class CompleteBookingView(APIView):
    permission_classes = [IsRole("provider", "admin")]

    def patch(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, provider_id=request.user.id)
        except (Booking.DoesNotExist, ValueError):
            return Response({"error": "Booking not found"}, status=404)
        _transition(booking, "completed")
        publish_event(
            "BookingCompleted",
            {**BookingSerializer(booking).data, "customerId": str(booking.customer_id), "providerId": str(booking.provider_id)},
        )
        return Response(BookingSerializer(booking).data)


class ConfirmBookingView(APIView):
    """Called by Payment Service (server-to-server) once payment is captured."""

    authentication_classes = []
    permission_classes = []

    def patch(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except (Booking.DoesNotExist, ValueError):
            return Response({"error": "Booking not found"}, status=404)
        if booking.status == "pending_payment":
            _transition(booking, "confirmed")
        return Response(BookingSerializer(booking).data)


class InternalBookingDetailView(APIView):
    """Used by Review Service to confirm a booking is completed and belongs
    to the reviewing customer before accepting a review."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except (Booking.DoesNotExist, ValueError):
            return Response({"error": "Booking not found"}, status=404)
        return Response(BookingSerializer(booking).data)
