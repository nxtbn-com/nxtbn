from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from django.db.models import Sum, Count


from nxtbn.core.admin_permissions import NxtbnAdminPermission
from nxtbn.order import OrderStatus
from nxtbn.order.models import Order, OrderLineItem
from nxtbn.payment.models import Payment
from .serializers import OrderSerializer
from nxtbn.core.paginator import NxtbnPagination

from babel.numbers import get_currency_precision


class OrderListView(generics.ListAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = NxtbnPagination


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'



class OrderStatsView(APIView):
    permission_classes = (NxtbnAdminPermission,)

    def get(self, request, *args, **kwargs):
        order_stats = Order.objects.aggregate(
            total_order_value=Sum('total_price'),
            total_orders=Count('id')
        )
        
        total_variant_orders = OrderLineItem.objects.aggregate(
            total=Count('variant', distinct=True)
        )['total'] or 0

        total_order_value_subunits = order_stats['total_order_value'] or 0
        precision = get_currency_precision(settings.BASE_CURRENCY)
        total_order_value_units = total_order_value_subunits / (10 ** precision)

        data = {
            'total_order_value': total_order_value_units,
            'total_orders': order_stats['total_orders'] or 0,
            'total_variant_orders': total_variant_orders
        }

        return Response(data)