from rest_framework import serializers

from .models import Invoice, Payout, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "type", "amount", "provider_reference", "succeeded", "created_at"]


class InvoiceSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id", "booking_id", "customer_id", "provider_id", "amount",
            "platform_fee", "status", "transactions", "created_at", "updated_at",
        ]


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = ["id", "provider_id", "amount", "period_start", "period_end", "status", "created_at"]
