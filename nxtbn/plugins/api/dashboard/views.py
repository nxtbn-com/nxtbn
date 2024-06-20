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

def get_module_path(module_name):
    spec = importlib.util.find_spec(module_name)
    if spec and spec.origin:
        absolute_path = os.path.dirname(spec.origin)
        # Calculate the relative path from BASE_DIR
        relative_path = os.path.relpath(absolute_path, start=settings.BASE_DIR)
        return relative_path
    raise ImportError(f"Module {module_name} not found")


def extract_metadata(file_path):
    metadata = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        inside_metadata = False
        for line in lines:
            if line.strip().startswith('metadata = {'):
                inside_metadata = True
            if inside_metadata:
                try:
                    key, value = line.split(':', 1)
                    key = key.strip().strip('"').strip("'")
                    value = value.strip().strip(',').strip('"').strip("'")
                    metadata[key] = value
                except ValueError:
                    continue
            if inside_metadata and line.strip().endswith('}'):
                break
    return metadata



class PluginBaseMixin:
    def handle_uploaded_file(self, file_path):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(self.tmpdirname)

        extracted_dirs = [d for d in os.listdir(self.tmpdirname) if os.path.isdir(os.path.join(self.tmpdirname, d))]
        logger.debug(f"Extracted directories: {extracted_dirs}")

        if len(extracted_dirs) != 1:
            raise ValidationError({'file': 'Unexpected directory structure in the ZIP file.'})

        source_dir = os.path.join(self.tmpdirname, extracted_dirs[0])
        init_file_path = os.path.join(source_dir, '__init__.py')
        if not os.path.exists(init_file_path):
            raise ValidationError({'file': '__init__.py file not found in the plugin directory.'})

        plugin_metadata = extract_metadata(init_file_path)
        plugin_name = plugin_metadata.get('plugin_name')
        plugin_type = plugin_metadata.get('plugin_type')
        nxtbn_version_compatibility = plugin_metadata.get('nxtbn_version_compatibility')

        if not plugin_name or not plugin_type:
            raise ValidationError({'file': 'Plugin name or type not found in metadata.'})

        if nxtbn_version_compatibility:
            current_version = parse_version(settings.VERSION)
            specifier = SpecifierSet(nxtbn_version_compatibility)
            if not current_version in specifier:
                shutil.rmtree(source_dir)
                raise ValidationError({'file': f'Plugin version {nxtbn_version_compatibility} is not compatible with the current version {settings.VERSION}.'})

        target_dir = os.path.join(get_module_path(PLUGIN_BASE_DIR), plugin_name)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.move(source_dir, target_dir)
        logger.debug(f"Target directory: {target_dir}")
        relative_path = os.path.relpath(target_dir, start=settings.BASE_DIR)

        requirements_path = os.path.join(target_dir, 'requirements.txt')
        if os.path.exists(requirements_path):
            subprocess.run(['pip', 'install', '-r', requirements_path], check=True)

        Plugin.objects.update_or_create(
            name=plugin_name,
            defaults={
                'description': plugin_metadata.get('description', ''),
                'path': relative_path,
                'plugin_type': plugin_type,
                'is_active': False,
                'home_url': plugin_metadata.get('plugin_uri', ''),
                'documentation_url': ''
            }
        )


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