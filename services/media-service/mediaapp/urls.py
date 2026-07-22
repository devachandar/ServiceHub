from django.urls import path

from . import views

urlpatterns = [
    path("upload", views.UploadView.as_view()),
    path("uploads/<str:filename>", views.ServeUploadView.as_view()),
]
