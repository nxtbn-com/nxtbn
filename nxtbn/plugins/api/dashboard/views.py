import importlib
import os
import zipfile
import shutil
import subprocess
import logging

from django.conf import settings
import tempfile

from django.forms import ValidationError
import requests
from nxtbn.plugins.utils import PluginHandler
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException

from rest_framework.views import APIView
from rest_framework.response import Response

from django.core.files.storage import FileSystemStorage
from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import JSONParser

from packaging.version import parse as parse_version
from packaging.specifiers import SpecifierSet


from nxtbn.plugins.models import fixed_dirs


from nxtbn.plugins import PluginType
from nxtbn.plugins.api.dashboard.serializers import  PluginInstallWithZIPURLSerializer, PluginSerializer, PluginUpdateSerializer, ZipFileUploadSerializer
from nxtbn.plugins.manager import PluginPathManager
from nxtbn.plugins.models import Plugin

logger = logging.getLogger(__name__)


PLUGIN_BASE_DIR = getattr(settings, 'PLUGIN_BASE_DIR')

os.makedirs(PLUGIN_BASE_DIR, exist_ok=True)



class PluginBaseMixin:
    def handle_uploaded_file(self, file_path):
        handler = PluginHandler()
        handler.handle_uploaded_file(file_path)


class PluginsUploadView(PluginBaseMixin, generics.CreateAPIView):
    serializer_class = ZipFileUploadSerializer

    def perform_create(self, serializer):
        uploaded_file = serializer.validated_data['file']
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.tmpdirname = tmpdirname
            temp_zip_path = os.path.join(tmpdirname, uploaded_file.name)
            with open(temp_zip_path, 'wb') as temp_zip_file:
                for chunk in uploaded_file.chunks():
                    temp_zip_file.write(chunk)
            self.handle_uploaded_file(temp_zip_path)

        return Response(
            {'message': 'ZIP file uploaded, extracted, and plugin registered successfully'},
            status=status.HTTP_201_CREATED,
        )

class PluginInstallViaZipUrlView(PluginBaseMixin, generics.CreateAPIView):
    serializer_class = PluginInstallWithZIPURLSerializer

    def perform_create(self, serializer):
        zip_url = serializer.validated_data['zip_url']
        response = requests.get(zip_url, stream=True)
        if response.status_code != 200:
            raise ValidationError({'zip_url': 'Failed to download the ZIP file.'})
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.tmpdirname = tmpdirname
            temp_zip_path = os.path.join(tmpdirname, 'plugin.zip')
            with open(temp_zip_path, 'wb') as temp_zip_file:
                for chunk in response.iter_content(chunk_size=128):
                    temp_zip_file.write(chunk)
            self.handle_uploaded_file(temp_zip_path)

        return Response(
            {'message': 'Plugin downloaded, extracted, and registered successfully'},
            status=status.HTTP_201_CREATED,
        )
    


class PluginDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'name'
    queryset = Plugin.objects.filter(has_deleted=False)
    serializer_class = PluginSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return self.serializer_class
        else:
            return PluginUpdateSerializer
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PluginPathManager.remove_plugins(instance.name, instance.plugin_type)
        
        # Mark the instance as deleted
        instance.has_deleted = True
        instance.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class UnregisteredPluginsAPIView(APIView):
    def get(self, request, format=None):
        plugin_base_dir = settings.PLUGIN_BASE_DIR
        all_directories = {name for name in os.listdir(plugin_base_dir) if os.path.isdir(os.path.join(plugin_base_dir, name))}
        
        registered_plugins = set(Plugin.objects.values_list('name', flat=True))
        
        unregistered_plugins = list(all_directories - registered_plugins)
        
        return Response(unregistered_plugins, status=status.HTTP_200_OK)
    

class PluginRegisterView(generics.CreateAPIView):
    queryset = Plugin.objects.all()
    serializer_class = PluginSerializer