from django.urls import path

from . import views

urlpatterns = [
    path("", views.CreateBookingView.as_view()),
    path("mine", views.MyBookingsView.as_view()),
    path("provider", views.ProviderBookingsView.as_view()),
    path("<str:booking_id>/cancel", views.CancelBookingView.as_view()),
    path("<str:booking_id>/reschedule", views.RescheduleBookingView.as_view()),
    path("<str:booking_id>/complete", views.CompleteBookingView.as_view()),
    path("<str:booking_id>/confirm", views.ConfirmBookingView.as_view()),
    path("internal/bookings/<str:booking_id>", views.InternalBookingDetailView.as_view()),
    path("availability/<str:provider_id>", views.AvailabilityView.as_view()),
]
