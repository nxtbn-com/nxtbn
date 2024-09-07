from django.conf import settings
import os

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.core.models import SiteSettings
from nxtbn.core.models import Site

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = "__all__"

class SiteSettingSerializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)
    class Meta:
        model = SiteSettings
        fields = "__all__"