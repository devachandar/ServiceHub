from django.http import JsonResponse
from django.urls import include, path


def health(request):
    return JsonResponse({"service": "provider_service", "status": "ok"})


urlpatterns = [
    path("health", health),
    path("", include("providers.urls")),
]
