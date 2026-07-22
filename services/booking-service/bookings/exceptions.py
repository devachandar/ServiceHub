from rest_framework.views import exception_handler


def friendly_exception_handler(exc, context):
    """Wraps DRF's default handler so every service returns the same
    { "error": "..." } shape the frontend expects, instead of DRF's default
    { "detail": "..." }."""
    response = exception_handler(exc, context)
    if response is not None and isinstance(response.data, dict) and "detail" in response.data:
        response.data = {"error": str(response.data["detail"])}
    return response
