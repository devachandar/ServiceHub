from django.db.models import Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation, Message
from .permissions import IsAuthenticatedStateless, IsRole
from .serializers import ConversationSerializer, MessageSerializer


class MyConversationsView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        qs = Conversation.objects.filter(Q(customer_id=request.user.id) | Q(provider_id=request.user.id)).order_by(
            "-created_at"
        )
        return Response(ConversationSerializer(qs, many=True).data)


class StartConversationView(APIView):
    """A customer opens a chat with a provider - optionally about a
    specific booking for context."""

    permission_classes = [IsRole("customer", "admin")]

    def post(self, request):
        provider_id = request.data.get("providerId")
        booking_id = request.data.get("bookingId")
        if not provider_id:
            return Response({"error": "providerId is required"}, status=400)

        existing = Conversation.objects.filter(
            customer_id=request.user.id, provider_id=provider_id, booking_id=booking_id
        ).first()
        if existing:
            return Response(ConversationSerializer(existing).data)

        conversation = Conversation.objects.create(
            customer_id=request.user.id, provider_id=provider_id, booking_id=booking_id
        )
        return Response(ConversationSerializer(conversation).data, status=201)


class ConversationMessagesView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request, conversation_id):
        conversation = self._get_conversation(request, conversation_id)
        if conversation is None:
            return Response({"error": "Conversation not found"}, status=404)
        messages = conversation.messages.order_by("created_at")
        return Response(MessageSerializer(messages, many=True).data)

    def post(self, request, conversation_id):
        """REST fallback for sending a message without a websocket
        connection - the websocket path is preferred for real-time delivery."""
        conversation = self._get_conversation(request, conversation_id)
        if conversation is None:
            return Response({"error": "Conversation not found"}, status=404)

        message = Message.objects.create(
            conversation=conversation,
            sender_id=request.user.id,
            sender_role=request.user.role,
            body=request.data.get("body", ""),
            attachment_url=request.data.get("attachmentUrl", ""),
        )
        return Response(MessageSerializer(message).data, status=201)

    def _get_conversation(self, request, conversation_id):
        try:
            return Conversation.objects.get(
                Q(id=conversation_id) & (Q(customer_id=request.user.id) | Q(provider_id=request.user.id))
            )
        except (Conversation.DoesNotExist, ValueError):
            return None


class MarkReadView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def patch(self, request, conversation_id):
        Message.objects.filter(
            conversation_id=conversation_id, read_at__isnull=True
        ).exclude(sender_id=request.user.id).update(read_at=timezone.now())
        return Response(status=204)
