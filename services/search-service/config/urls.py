from django.http import JsonResponse
from django.urls import include, path


def health(request):
    return JsonResponse({"service": "search_service", "status": "ok"})


urlpatterns = [
    path("health", health),
    path("", include("search_app.urls")),
]
