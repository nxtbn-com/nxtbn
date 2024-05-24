from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException

from nxtbn.core.admin_permissions import NxtbnAdminPermission
from nxtbn.payment.models import Payment
from nxtbn.payment.api.dashboard.serializers import RefundSerializer

class RefundAPIView(generics.UpdateAPIView):
    permission_classes = (NxtbnAdminPermission,)
    queryset = Payment.objects.all()
    serializer_class = RefundSerializer

    def get_object(self):
        order_alias = self.kwargs.get('order_alias')
        return get_object_or_404(Payment, order__alias=order_alias)