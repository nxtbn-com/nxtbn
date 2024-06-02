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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        payment_plugin_id = self.context.get('payment_plugin_id')
        if payment_plugin_id:
            self.fields['special_data'] = PaymentManager(payment_plugin_id).special_serializer()
            self.fields['special_data'].write_only = True

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
        special_data = validated_data.pop('special_data', {})

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
    
    # def get_meta_data(self, obj):
    #     meta_data = PaymentManager(
    #         self.context.get('payment_plugin_id'),
    #         self.context,
    #         order_instance=obj
    #     ).payment_url_with_meta(
    #         order_alias=obj.alias,
    #         order_instance=obj
    #     )
    #     return meta_data

    # Do we still need this? 
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
        
    #     meta_data = PaymentManager(
    #         self.context.get('payment_plugin_id',
    #         self.context,
    #     )).payment_url_with_meta(
    #         order_alias=instance.alias,
    #         order_instance=instance
    #     )
    #     # Include 'meta_data' in the response
    #     representation['meta_data'] = meta_data
    #     return representation

    

class AuthenticatedUserOrderSerializer(serializers.ModelSerializer): # TO DO: Test with frontend passing both saved address id and promo code etc?
    currency_code = serializers.CharField(write_only=True, required=False)
    promo_code= serializers.CharField(write_only=True, required=False)
    cart_data = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    meta_data =  serializers.ListField(child=serializers.DictField(), write_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        payment_plugin_id = self.context.get('payment_plugin_id')
        if payment_plugin_id:
            self.fields['special_data'] = PaymentManager(payment_plugin_id).special_serializer()

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

        payment = Payment.objects.create(
            order=order,
            payment_plugin_id=getway,
            payment_method= PaymentMethod.CASH_ON_DELIVERY if validated_data.get('getway') else PaymentMethod.CREDIT_CARD,
            gateway_response_raw=meta_data
        )
        payment.authorize_payment(
            validated_data.get('amount'),
            order.id,
        )
        

        for item in cart_data:
            order.line_items.create(**item)

        return order