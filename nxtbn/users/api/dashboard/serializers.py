from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction


class DashboardLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)