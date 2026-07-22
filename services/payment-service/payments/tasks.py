import random

from celery import shared_task

from .events import publish_event
from .models import Invoice, Transaction

PLATFORM_FEE_RATE = 0.1


@shared_task(bind=True, max_retries=5, default_retry_delay=10)
def create_invoice_task(self, booking_payload):
    """Runs via Celery/RabbitMQ (not inline in the request path) so a
    transient DB blip on BookingCreated gets retried automatically instead
    of silently dropping the invoice."""
    booking_id = booking_payload["id"]
    if Invoice.objects.filter(booking_id=booking_id).exists():
        return

    amount = booking_payload["price"]
    fee = round(float(amount) * PLATFORM_FEE_RATE, 2)
    Invoice.objects.create(
        booking_id=booking_id,
        customer_id=booking_payload["customerId"],
        provider_id=booking_payload["providerId"],
        amount=amount,
        platform_fee=fee,
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def capture_payment_task(self, invoice_id):
    """Simulates calling a real payment gateway (Stripe/Braintree). No real
    card processing happens here - this is a stand-in so the booking flow
    is fully demoable without a payments account, while still exercising
    Celery's retry/backoff behavior a real integration would rely on."""
    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return

    if invoice.status == "paid":
        return

    if random.random() < 0.05:
        raise self.retry(exc=Exception("Simulated gateway timeout"))

    invoice.status = "paid"
    invoice.save(update_fields=["status", "updated_at"])
    Transaction.objects.create(
        invoice=invoice, type="charge", amount=invoice.amount, provider_reference=f"sim_{invoice.id.hex[:12]}"
    )

    publish_event(
        "PaymentCaptured",
        {
            "invoiceId": str(invoice.id),
            "bookingId": str(invoice.booking_id),
            "customerId": str(invoice.customer_id),
            "providerId": str(invoice.provider_id),
            "amount": str(invoice.amount),
        },
    )

    import requests
    from django.conf import settings

    try:
        requests.patch(f"{settings.INTERNAL_SERVICE_URLS['booking']}/{invoice.booking_id}/confirm", timeout=5)
    except requests.RequestException:
        pass
