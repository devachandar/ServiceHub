from decimal import Decimal

from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView

from .events import publish_event
from .models import Invoice, Transaction
from .permissions import IsAuthenticatedStateless, IsRole
from .serializers import InvoiceSerializer
from .tasks import capture_payment_task


class MyInvoicesView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        qs = Invoice.objects.filter(customer_id=request.user.id).order_by("-created_at")
        return Response(InvoiceSerializer(qs, many=True).data)


class ProviderInvoicesView(APIView):
    permission_classes = [IsRole("provider", "admin")]

    def get(self, request):
        qs = Invoice.objects.filter(provider_id=request.user.id).order_by("-created_at")
        return Response(InvoiceSerializer(qs, many=True).data)


class ProviderEarningsView(APIView):
    """Backs the provider's "View earnings" dashboard requirement."""

    permission_classes = [IsRole("provider", "admin")]

    def get(self, request):
        invoices = Invoice.objects.filter(provider_id=request.user.id, status="paid")
        gross = invoices.aggregate(total=Sum("amount"))["total"] or Decimal("0")
        fees = invoices.aggregate(total=Sum("platform_fee"))["total"] or Decimal("0")
        return Response(
            {
                "grossEarnings": str(gross),
                "platformFees": str(fees),
                "netEarnings": str(gross - fees),
                "paidInvoiceCount": invoices.count(),
            }
        )


class InvoiceByBookingView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request, booking_id):
        try:
            invoice = Invoice.objects.get(booking_id=booking_id)
        except (Invoice.DoesNotExist, ValueError):
            return Response({"error": "No invoice for this booking yet"}, status=404)
        if (
            str(invoice.customer_id) != str(request.user.id)
            and str(invoice.provider_id) != str(request.user.id)
            and request.user.role != "admin"
        ):
            return Response({"error": "Not your invoice"}, status=403)
        return Response(InvoiceSerializer(invoice).data)


class PayInvoiceView(APIView):
    """Customer confirms payment on a pending invoice - kicks off the
    (retry-capable) Celery capture task rather than blocking the request on
    a real gateway call."""

    permission_classes = [IsRole("customer", "admin")]

    def post(self, request, invoice_id):
        try:
            invoice = Invoice.objects.get(id=invoice_id, customer_id=request.user.id)
        except (Invoice.DoesNotExist, ValueError):
            return Response({"error": "Invoice not found"}, status=404)
        if invoice.status == "paid":
            return Response({"error": "This invoice is already paid"}, status=400)

        capture_payment_task.delay(str(invoice.id))
        return Response({"status": "processing"}, status=202)


class RefundInvoiceView(APIView):
    permission_classes = [IsRole("provider", "admin")]

    def post(self, request, invoice_id):
        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except (Invoice.DoesNotExist, ValueError):
            return Response({"error": "Invoice not found"}, status=404)
        if request.user.role != "admin" and str(invoice.provider_id) != str(request.user.id):
            return Response({"error": "Not your invoice"}, status=403)
        if invoice.status != "paid":
            return Response({"error": "Only a paid invoice can be refunded"}, status=400)

        amount = Decimal(str(request.data.get("amount", invoice.amount)))
        invoice.status = "refunded" if amount >= invoice.amount else "partially_refunded"
        invoice.save(update_fields=["status", "updated_at"])
        Transaction.objects.create(invoice=invoice, type="refund", amount=amount)

        publish_event(
            "RefundIssued",
            {"invoiceId": str(invoice.id), "bookingId": str(invoice.booking_id), "amount": str(amount)},
        )
        return Response(InvoiceSerializer(invoice).data)
