from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.order.models import Address, Order, OrderLineItem
from nxtbn.payment import PaymentMethod
from nxtbn.payment.models import Payment
from nxtbn.payment.payment_manager import PaymentManager

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        exclude=['user']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLineItem
        exclude = ('order',)

class OrderSerializer(serializers.ModelSerializer):
    line_item = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = '__all__'
        ref_name = 'order_storefront_get'



class GuestOrderSerializer(serializers.ModelSerializer):
    currency_code = serializers.CharField(write_only=True, required=False)
    promo_code= serializers.CharField(write_only=True, required=False)
    shipping_address = AddressSerializer(write_only=True)
    billing_address = AddressSerializer(write_only=True, required=False)
    cart_data = OrderItemSerializer(many=True, write_only=True)
    total_price = serializers.DecimalField(write_only=True, max_digits=12, decimal_places=3) # accepting in unit and soring in subunit

    class Meta:
        model = Order
        fields = [
            'currency_code',
            'promo_code',
            'total_price',
            'shipping_address',
            'billing_address',
            'cart_data',
            'meta_data',
        ]
    
    def create(self, validated_data):
        promo_code = validated_data.pop('promo_code', None)
        cart_data = validated_data.pop('cart_data')
        # special_data = validated_data.pop('special_data', {})

        shipping_address_data = validated_data.pop('shipping_address')
        billing_address_data = validated_data.pop('billing_address')

        shipping_address= Address.objects.create(**shipping_address_data)
        billing_address = Address.objects.create(**billing_address_data)

        order = Order.objects.create(
            shipping_address=shipping_address,
            billing_address=billing_address,
            **validated_data
        )

        for item in cart_data:
            order.line_items.create(**item)

        return order


class AuthenticatedUserOrderSerializer(serializers.ModelSerializer): # TO DO: Test with frontend passing both saved address id and promo code etc?
    currency_code = serializers.CharField(write_only=True, required=False)
    promo_code= serializers.CharField(write_only=True, required=False)
    cart_data = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    meta_data =  serializers.ListField(child=serializers.DictField(), write_only=True, required=False)


    class Meta:
        model = Order
        fields = [
            'promo_code',
            'total_price',
            'shipping_address',
            'billing_address',
            'cart_data',
            'meta_data',
            'currency_code',
        ]
    
    def create(self, validated_data):
        getway = validated_data.pop('getway')
        promo_code = validated_data.pop('promo_code', None)
        cart_data = validated_data.pop('cart_data')
        meta_data = validated_data.pop('meta_data', {})

        shipping_address_data = validated_data.pop('shipping_address')
        billing_address_data = validated_data.pop('billing_address')

        shipping_address= Address.objects.create(**shipping_address_data)
        billing_address = Address.objects.create(**billing_address_data)


        order = Order.objects.create(
            shipping_address=shipping_address,
            billing_address=billing_address,
            **validated_data
        )
        

        for item in cart_data:
            order.line_items.create(**item)

        return order