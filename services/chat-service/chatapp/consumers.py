import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"conversation_{self.conversation_id}"
        user = self.scope.get("user")

        if not user:
            await self.close(code=4001)
            return

        allowed = await self.is_participant(self.conversation_id, user.id)
        if not allowed:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        body = data.get("body", "")
        attachment_url = data.get("attachmentUrl", "")
        user = self.scope["user"]

        message = await self.save_message(self.conversation_id, user.id, user.role, body, attachment_url)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": {
                    "id": str(message.id),
                    "senderId": str(message.sender_id),
                    "senderRole": message.sender_role,
                    "body": message.body,
                    "attachmentUrl": message.attachment_url,
                    "createdAt": message.created_at.isoformat(),
                },
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def is_participant(self, conversation_id, user_id):
        return Conversation.objects.filter(id=conversation_id).filter(Q(customer_id=user_id) | Q(provider_id=user_id)).exists()

    @database_sync_to_async
    def save_message(self, conversation_id, sender_id, sender_role, body, attachment_url):
        return Message.objects.create(
            conversation_id=conversation_id,
            sender_id=sender_id,
            sender_role=sender_role,
            body=body,
            attachment_url=attachment_url,
        )
