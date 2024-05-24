from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.order import OrderStatus
from nxtbn.order.models import Order
from nxtbn.payment.models import Payment

class RefundSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(write_only=True, max_digits=4, decimal_places=2)
    class Meta:
        model = Payment
        fields = ['amount']

    def update(self, instance, validated_data):
        amount = validated_data.get('amount', '') # if null, then full refund, if amount, partial refund
        instance.refund_payment(amount)
        return instance
