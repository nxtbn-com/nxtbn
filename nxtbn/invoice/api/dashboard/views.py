from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException
from nxtbn.core.models import SiteSettings
from nxtbn.order.models import Order


class InvoiceListCreateView(generics.ListCreateAPIView):
    def create(self, request, *args, **kwargs):
        pass

class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'