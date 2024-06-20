from django.conf import settings
import os

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.plugins import PluginType
from nxtbn.plugins.manager import PluginPathManager
from nxtbn.plugins.models import Plugin

class ZipFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    # plugin_type = serializers.ChoiceField(choices=PluginType.choices)
    
    def validate_file(self, value):
        valid_extensions = ['.zip',]
        ext = os.path.splitext(value.name)[1].lower()
        
        if ext not in valid_extensions:
            raise serializers.ValidationError(f"Invalid file extension: {ext}.")
        
        if value.size > 5 * 1024 * 1024:  # 5 MB
            raise serializers.ValidationError("File is too large. Maximum size is 5 MB.")

        return value



class PluginInstallWithZIPURLSerializer(serializers.Serializer):
    zip_url = serializers.URLField()
    # plugin_type = serializers.ChoiceField(choices=PluginType.choices)
    # tag = serializers.CharField(max_length=255, required=False) # version tag



class PluginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plugin
        exclude = ['has_deleted', 'is_active']

    def create(self, validated_data):
        plugin_name = validated_data.get('name')
        plugin_base_dir = settings.PLUGIN_BASE_DIR

        # Check if the directory exists in PLUGIN_BASE_DIR
        plugin_dir = os.path.join(plugin_base_dir, plugin_name)
        if not os.path.isdir(plugin_dir):
            raise serializers.ValidationError(f"Directory '{plugin_name}' does not exist in {plugin_base_dir}.")

        # Check if the plugin is already registered
        if Plugin.objects.filter(name=plugin_name).exists():
            raise serializers.ValidationError(f"Plugin '{plugin_name}' is already registered.")

        # Proceed with creating the Plugin instance
        return super().create(validated_data)


class PluginUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plugin
        fields = ['is_active']

    def update(self, instance, validated_data):
        instance.is_active = validated_data['is_active']
        instance.save()

        if instance.is_active:
            PluginPathManager.cache_plugin_path(instance)
        else:
            PluginPathManager.remove_plugin_from_cache(instance)

        return instance