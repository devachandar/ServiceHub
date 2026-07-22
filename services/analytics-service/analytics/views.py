from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DailyMetric, ProviderMetric
from .permissions import IsRole


class KPISummaryView(APIView):
    """Backs the admin "View analytics" requirement - growth, revenue,
    bookings over the trailing 30 days."""

    permission_classes = [IsRole("admin")]

    def get(self, request):
        since = timezone.now().date() - timedelta(days=30)
        rows = DailyMetric.objects.filter(date__gte=since).order_by("date")

        totals = rows.aggregate(
            bookings_created=Sum("bookings_created"),
            bookings_completed=Sum("bookings_completed"),
            bookings_cancelled=Sum("bookings_cancelled"),
            revenue=Sum("revenue"),
            new_reviews=Sum("new_reviews"),
            new_users=Sum("new_users"),
        )

        daily = [
            {
                "date": row.date.isoformat(),
                "bookingsCreated": row.bookings_created,
                "bookingsCompleted": row.bookings_completed,
                "bookingsCancelled": row.bookings_cancelled,
                "revenue": str(row.revenue),
                "newReviews": row.new_reviews,
                "newUsers": row.new_users,
            }
            for row in rows
        ]

        return Response({"totals": {k: (str(v) if k == "revenue" else (v or 0)) for k, v in totals.items()}, "daily": daily})


class TopProvidersView(APIView):
    permission_classes = [IsRole("admin")]

    def get(self, request):
        qs = ProviderMetric.objects.order_by("-total_revenue")[:20]
        return Response(
            [
                {
                    "providerId": str(p.provider_id),
                    "totalBookings": p.total_bookings,
                    "totalRevenue": str(p.total_revenue),
                    "totalReviews": p.total_reviews,
                }
                for p in qs
            ]
        )
