from django.urls import path

from . import views

urlpatterns = [
    path("mine", views.MyInvoicesView.as_view()),
    path("provider", views.ProviderInvoicesView.as_view()),
    path("provider/earnings", views.ProviderEarningsView.as_view()),
    path("booking/<str:booking_id>", views.InvoiceByBookingView.as_view()),
    path("<str:invoice_id>/pay", views.PayInvoiceView.as_view()),
    path("<str:invoice_id>/refund", views.RefundInvoiceView.as_view()),
]
