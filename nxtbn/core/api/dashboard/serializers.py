from django.conf import settings
import os

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.core import PluginType

class ZipFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        valid_extensions = ['.zip',]
        ext = os.path.splitext(value.name)[1].lower()
        
        if ext not in valid_extensions:
            raise serializers.ValidationError(f"Invalid file extension: {ext}.")
        
        if value.size > 5 * 1024 * 1024:  # 5 MB
            raise serializers.ValidationError("File is too large. Maximum size is 5 MB.")

        return value


class PluginInstallSerializer(serializers.Serializer):
    git_url = serializers.URLField()
    plugin_type = serializers.ChoiceField(choices=PluginType.choices)