import uuid

from django.db import models


class Conversation(models.Model):
    """Chat Service owns: messages, read status, attachments. A
    conversation is just a (customer, provider) pair, optionally tied to a
    specific booking for context."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.UUIDField()
    provider_id = models.UUIDField()
    booking_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender_id = models.UUIDField()
    sender_role = models.CharField(max_length=20)
    body = models.TextField(blank=True, default="")
    attachment_url = models.URLField(blank=True, default="")
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
