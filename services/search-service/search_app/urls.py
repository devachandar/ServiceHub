from django.urls import path

from . import views

urlpatterns = [
    path("", views.SearchView.as_view()),
    path("autocomplete", views.AutocompleteView.as_view()),
]
