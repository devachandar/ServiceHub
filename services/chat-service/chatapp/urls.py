from django.urls import path

from . import views

urlpatterns = [
    path("conversations", views.MyConversationsView.as_view()),
    path("conversations/start", views.StartConversationView.as_view()),
    path("conversations/<str:conversation_id>/messages", views.ConversationMessagesView.as_view()),
    path("conversations/<str:conversation_id>/read", views.MarkReadView.as_view()),
]
