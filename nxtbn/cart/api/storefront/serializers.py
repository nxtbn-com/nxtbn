from rest_framework import serializers
from nxtbn.cart.models import CartItem
from nxtbn.product.api.dashboard.serializers import ProductVariantSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantSerializer()
    class Meta:
        model = CartItem
        fields = '__all__'