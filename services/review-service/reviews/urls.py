from django.urls import path

from . import views

urlpatterns = [
    path("", views.CreateReviewView.as_view()),
    path("mine", views.MyReviewsView.as_view()),
    path("provider/<str:provider_id>", views.ProviderReviewsView.as_view()),
    path("<str:review_id>/respond", views.RespondToReviewView.as_view()),
    path("admin/<str:review_id>/moderate", views.AdminModerateReviewView.as_view()),
]
