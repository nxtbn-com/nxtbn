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





class OrderCreateAPIView(generics.CreateAPIView):
    """
    API endpoint to create an authenticated user order.

    This view allows authenticated users to create orders. The serializer used for the order creation
    is determined dynamically based on the payment gateway ID provided in the URL.
    """

    serializer_class = AuthenticatedUserOrderSerializer