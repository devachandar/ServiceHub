from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProviderListView.as_view()),
    path("onboard", views.OnboardProviderView.as_view()),
    path("me", views.MyProviderProfileView.as_view()),
    path("me/services", views.ServiceListCreateView.as_view()),
    path("me/services/<str:service_id>", views.ServiceDetailView.as_view()),
    path("me/working-hours", views.WorkingHoursView.as_view()),
    path("me/time-off", views.TimeOffView.as_view()),
    path("me/portfolio", views.PortfolioView.as_view()),
    path("me/verification-documents", views.VerificationDocumentView.as_view()),
    path("internal/providers/<str:provider_id>", views.InternalProviderDetailView.as_view()),
    path("internal/providers/<str:provider_id>/rating", views.InternalRatingUpdateView.as_view()),
    path("admin/providers", views.AdminProviderListView.as_view()),
    path("admin/providers/<str:provider_id>/verify", views.AdminVerifyProviderView.as_view()),
    path("<str:provider_id>", views.ProviderDetailView.as_view()),
]
