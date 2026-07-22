from django.urls import path

from . import views

urlpatterns = [
    path("register", views.RegisterView.as_view()),
    path("login", views.LoginView.as_view()),
    path("refresh", views.RefreshView.as_view()),
    path("logout", views.LogoutView.as_view()),
    path("me", views.MeView.as_view()),
    path("internal/users/<str:user_id>", views.InternalUserDetailView.as_view()),
    path("admin/users", views.AdminUserListView.as_view()),
    path("admin/users/<str:user_id>/status", views.AdminUserStatusView.as_view()),
]
