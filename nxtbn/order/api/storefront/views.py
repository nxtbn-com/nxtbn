import os
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException
from rest_framework.views import APIView

from nxtbn.core.paginator import NxtbnPagination
from nxtbn.order.api.storefront.serializers import AuthenticatedUserOrderSerializer, OrderSerializer, GuestOrderSerializer
from nxtbn.order.models import Order
from nxtbn.order import OrderStatus
from django.conf import settings

from nxtbn.payment import PaymentStatus
from nxtbn.payment.models import Payment
from nxtbn.payment.payment_manager import PaymentManager
from nxtbn.payment.utils import check_plugin_directory
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class OrderListView(generics.ListAPIView):
    pagination_class = NxtbnPagination
    serializer_class = OrderSerializer

    def get_queryset(self):
        return  Order.objects.filter(id=self.request.user)
    


class GuestUserOrderCreateAPIView(generics.CreateAPIView):
    """
    API endpoint to create an anonymous user order.

    This view allows anonymous users to create orders. The serializer used for the order creation
    is determined dynamically based on the payment gateway ID provided in the URL.
    """

    permission_classes = (AllowAny,)
    serializer_class = GuestOrderSerializer

    @swagger_auto_schema(
        responses={
            201: openapi.Response(
                description="Order created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'promo_code': openapi.Schema(type=openapi.TYPE_STRING),
                        'total_price': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'shipping_address': openapi.Schema(type=openapi.TYPE_OBJECT),  # Adjust according to your AddressSerializer schema
                        'billing_address': openapi.Schema(type=openapi.TYPE_OBJECT),   # Adjust according to your AddressSerializer schema
                        'cart_data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),  # Adjust according to your OrderItemSerializer schema
                        'meta_data': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            )
        }
    )

    def get_serializer_context(self):
        """
        Get the serializer context with the payment gateway ID.

        This method retrieves the payment gateway ID from the URL kwargs and adds it to the serializer context.
        """
        context = super().get_serializer_context()
        payment_plugin_id = self.kwargs.get('payment_plugin_id')
        if payment_plugin_id:
            context['payment_plugin_id'] = payment_plugin_id
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch the request.

        This method validates whether the provided payment gateway ID matches any defined payment gateway
        in the settings. If not, it raises a 404 error.
        """
        payment_plugin_id = self.kwargs.get('payment_plugin_id')
        if payment_plugin_id:
            if not  check_plugin_directory(payment_plugin_id):
                raise Http404(f"Payment gateway '{payment_plugin_id}' is not installed plugin.")
        return super().dispatch(request, *args, **kwargs)



class OrderCreateAPIView(generics.CreateAPIView):
    """
    API endpoint to create an authenticated user order.

    This view allows authenticated users to create orders. The serializer used for the order creation
    is determined dynamically based on the payment gateway ID provided in the URL.
    """

    serializer_class = AuthenticatedUserOrderSerializer

    def get_serializer_context(self):
        """
        Get the serializer context with the payment gateway ID.

        This method retrieves the payment gateway ID from the URL kwargs and adds it to the serializer context.
        """
        context = super().get_serializer_context()
        payment_plugin_id = self.kwargs.get('payment_plugin_id')
        if payment_plugin_id:
            context['payment_plugin_id'] = payment_plugin_id
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch the request.

        This method validates whether the provided payment gateway ID matches any defined payment gateway
        in the settings. If not, it raises a 404 error.
        """
        payment_plugin_id = self.kwargs.get('payment_plugin_id')
        if payment_plugin_id:
            if payment_plugin_id.lower() not in getattr(settings, 'PAYMENT_GATEWAYS'):
                raise Http404(f"Payment gateway '{payment_plugin_id}' is not implemented.")
        return super().dispatch(request, *args, **kwargs)