from django.urls import path

from . import views

urlpatterns = [
    path("me", views.MyProfileView.as_view()),
    path("internal/profiles/<str:user_id>", views.InternalProfileDetailView.as_view()),
    path("addresses", views.AddressListCreateView.as_view()),
    path("addresses/<str:address_id>", views.AddressDetailView.as_view()),
    path("saved-providers", views.SavedProviderListView.as_view()),
    path("saved-providers/<str:provider_id>", views.SavedProviderDetailView.as_view()),
    path("preferences", views.PreferenceView.as_view()),
]
