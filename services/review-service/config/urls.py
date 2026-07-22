from django.http import JsonResponse
from django.urls import include, path


def health(request):
    return JsonResponse({"service": "review_service", "status": "ok"})


urlpatterns = [
    path("health", health),
    path("", include("reviews.urls")),
]
