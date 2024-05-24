from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction


from nxtbn.order import OrderStatus
from nxtbn.order.models import Order, OrderLineItem
from nxtbn.payment.models import Payment



class OrderLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLineItem
        fields = ('id', 'variant', 'quantity', 'price_per_unit', 'total_price',)


class OrderSerializer(serializers.ModelSerializer):
    line_items = OrderLineItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()
    vendor = serializers.StringRelatedField(allow_null=True)
    shipping_address = serializers.StringRelatedField(allow_null=True)
    billing_address = serializers.StringRelatedField(allow_null=True)
    promo_code = serializers.StringRelatedField(allow_null=True)
    gift_card = serializers.StringRelatedField(allow_null=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'vendor',
            'payment_method',
            'shipping_address',
            'billing_address',
            'total_price',
            'status',
            'authorize_status',
            'charge_status',
            'promo_code',
            'gift_card',
            'line_items',
        )
