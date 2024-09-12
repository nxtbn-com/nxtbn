from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from django.db.models import Sum, Count, F
from django.utils import timezone

from datetime import timedelta

from decimal import Decimal

from rest_framework import filters as drf_filters
import django_filters
from django_filters import rest_framework as filters

from nxtbn.core.admin_permissions import NxtbnAdminPermission
from nxtbn.order import OrderAuthorizationStatus, OrderChargeStatus, OrderStatus
from nxtbn.order.models import Order, OrderLineItem
from nxtbn.payment import PaymentMethod
from nxtbn.payment.models import Payment
from nxtbn.product.models import ProductVariant
from .serializers import OrderListSerializer, OrderSerializer
from nxtbn.core.paginator import NxtbnPagination

from babel.numbers import get_currency_precision



class OrderFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=OrderStatus.choices)
    charge_status = filters.ChoiceFilter(choices=OrderChargeStatus.choices)
    authorize_status = filters.ChoiceFilter(choices=OrderAuthorizationStatus.choices)
    currency = filters.CharFilter(field_name='currency', lookup_expr='iexact')
    payment_method = filters.ChoiceFilter(choices=PaymentMethod.choices)
    start_date = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Order
        fields = [
            'status',
            'charge_status',
            'authorize_status',
            'currency',
            'payment_method',
            'start_date',
            'end_date'
        ]


class OrderListView(generics.ListAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    pagination_class = NxtbnPagination

    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter
    ]
    filterset_class = OrderFilter
    search_fields = ['order_number', 'user__username', 'supplier__name']
    ordering_fields = ['created_at']


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'



# class OrderStatsView(APIView):
#     permission_classes = (NxtbnAdminPermission,)

#     def get(self, request, *args, **kwargs):
#         order_stats = Order.objects.aggregate(
#             total_order_value=Sum('total_price'),
#             total_orders=Count('id')
#         )
        
#         total_variant_orders = OrderLineItem.objects.aggregate(
#             total=Count('variant', distinct=True)
#         )['total'] or 0

#         total_order_value_subunits = order_stats['total_order_value'] or 0
#         precision = get_currency_precision(settings.BASE_CURRENCY)
#         total_order_value_units = total_order_value_subunits / (10 ** precision)

#         data = {
#             'total_order_value': total_order_value_units,
#             'total_orders': order_stats['total_orders'] or 0,
#             'total_variant_orders': total_variant_orders
#         }

#         return Response(data)
    

class BasicStatsView(APIView):

    def get(self, request):
        today = timezone.now()
        last_week = today - timedelta(days=7)

        # Total Orders
        total_orders = Order.objects.count()
        orders_last_week = Order.objects.filter(created_at__gte=last_week).count()
        orders_last_week_percentage_change = (orders_last_week / total_orders) * 100 if total_orders > 0 else 0

        # Total Variants
        total_variants = ProductVariant.objects.count()

        # Total Sale (sum of total_price in Orders)
        total_sale = Order.objects.aggregate(total=Sum(F('total_price') / Decimal(100)))['total'] or Decimal(0)
        sales_last_week = Order.objects.filter(created_at__gte=last_week).aggregate(total=Sum(F('total_price') / Decimal(100)))['total'] or Decimal(0)
        sales_last_week_percentage_change = (sales_last_week / total_sale) * 100 if total_sale > 0 else 0

        # Net Sales (sum of payment_amount in Payments)
        net_sales = Payment.objects.aggregate(net_total=Sum(F('payment_amount') / Decimal(100)))['net_total'] or Decimal(0)
        net_sales_last_week = Payment.objects.filter(created_at__gte=last_week).aggregate(net_total=Sum(F('payment_amount') / Decimal(100)))['net_total'] or Decimal(0)
        net_sales_last_week_percentage_change = (net_sales_last_week / net_sales) * 100 if net_sales > 0 else 0

        # Prepare the response data
        data = {
            'sales': {
                'amount': total_sale,
                'last_percentage_change': sales_last_week_percentage_change
            },
            'orders': {
                'amount': total_orders,
                'last_percentage_change': orders_last_week_percentage_change
            },
            'variants': {
                'amount': total_variants,
            },
            'net_sales': {
                'amount': net_sales,
                'last_percentage_change': net_sales_last_week_percentage_change
            }
        }
        
        return Response(data)