from django.urls import path

from . import views

urlpatterns = [
    path("kpis", views.KPISummaryView.as_view()),
    path("top-providers", views.TopProvidersView.as_view()),
]
