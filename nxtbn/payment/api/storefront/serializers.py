from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.payment.models import Payment

from rest_framework import serializers
from nxtbn.order.models import Order
from nxtbn.payment.payment_manager import PaymentManager

class PaymentUrlSerializer(serializers.Serializer):
    order_alias = serializers.CharField()