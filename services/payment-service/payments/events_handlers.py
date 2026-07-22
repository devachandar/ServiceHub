from .tasks import create_invoice_task


def handle_booking_created(payload):
    create_invoice_task.delay(payload)


HANDLERS = {
    "BookingCreated": handle_booking_created,
}
