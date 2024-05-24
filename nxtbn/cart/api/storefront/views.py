from rest_framework import generics
from rest_framework.response import Response
from nxtbn.cart.models import CartItem
from nxtbn.cart.api.storefront.serializers import CartItemSerializer

class CartItemListView(generics.ListAPIView):
    """
    API endpoint for listing all carts.
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
