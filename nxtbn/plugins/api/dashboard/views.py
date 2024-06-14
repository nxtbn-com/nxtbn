import importlib
import os
import zipfile
import shutil
import subprocess

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

from rest_framework import serializers




from nxtbn.plugins import PluginType
from nxtbn.plugins.api.dashboard.serializers import PluginInstallSerializer, PluginInstallWithZIPURLSerializer, ZipFileUploadSerializer
from nxtbn.plugins.models import Plugin

PLUGIN_BASE_DIR = getattr(settings, 'PLUGIN_BASE_DIR')

os.makedirs(PLUGIN_BASE_DIR, exist_ok=True)

def get_module_path(module_name):
    spec = importlib.util.find_spec(module_name)
    if spec and spec.origin:
        return os.path.dirname(spec.origin)
    raise ImportError(f"Module {module_name} not found")


class PlugginsInstallViaGitView(generics.CreateAPIView):
    serializer_class = PluginInstallSerializer

    def perform_create(self, serializer):
        git_url = serializer.validated_data['git_url']
        plugin_type = serializer.validated_data['plugin_type']
        
        # Determine the target directory based on the plugin type
        target_dir_base = get_module_path(PLUGIN_BASE_DIR)
        
        # Clone the repository
        with tempfile.TemporaryDirectory() as tmpdirname:
            clone_dir = os.path.join(tmpdirname, 'repo')
            subprocess.run(['git', 'clone', git_url, clone_dir], check=True)

            # Remove the .git directory
            git_dir = os.path.join(clone_dir, '.git')
            if os.path.exists(git_dir):
                shutil.rmtree(git_dir)
            
            # Move the cloned directory to the target directory
            plugin_name = os.path.basename(git_url).rsplit('.', 1)[0]
            target_dir = os.path.join(target_dir_base, plugin_name)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.move(clone_dir, target_dir)

            # Install requirements if requirements.txt exists
            requirements_path = os.path.join(target_dir, 'requirements.txt')
            if os.path.exists(requirements_path):
                subprocess.run(['pip', 'install', '-r', requirements_path], check=True)
            
            # Create or update the plugin record in the database
            Plugin.objects.update_or_create(
                name=plugin_name,
                defaults={
                    'description': '',
                    'path': target_dir,
                    'plugin_type': plugin_type,
                    'is_active': False,
                    'home_url': git_url,
                    'documentation_url': git_url
                }
            )

        return Response(
            {'message': 'Plugin cloned, .git removed, and requirements installed successfully'},
            status=status.HTTP_201_CREATED,
        )


class PlugginsUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ZipFileUploadSerializer(data=request.data)

        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            plugin_type = serializer.validated_data['plugin_type']

            # Ensure the plugin_type is valid
            if plugin_type not in PluginType.values:
                raise ValidationError({'plugin_type': 'Invalid plugin type.'})

            # Save the uploaded file temporarily
            with tempfile.TemporaryDirectory() as tmpdirname:
                temp_zip_path = os.path.join(tmpdirname, uploaded_file.name)
                with open(temp_zip_path, 'wb') as temp_zip_file:
                    for chunk in uploaded_file.chunks():
                        temp_zip_file.write(chunk)

                # Extract the ZIP file
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdirname)

                # Determine the plugin name and target directory
                plugin_name = os.path.splitext(uploaded_file.name)[0]
                source_dir = os.path.join(tmpdirname, plugin_name)
                target_dir = os.path.join(PLUGIN_BASE_DIR, plugin_name)

                # Move the extracted files to the target directory
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                shutil.move(source_dir, target_dir)

                # Create or update the plugin record in the database
                Plugin.objects.update_or_create(
                    name=plugin_name,
                    defaults={
                        'description': '',
                        'path': target_dir,
                        'plugin_type': plugin_type,
                        'is_active': False,
                        'home_url': '',
                        'documentation_url': ''
                    }
                )

            return Response(
                {'message': 'ZIP file uploaded, extracted, and plugin registered successfully'},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class PluginInstallViaZipUrlView(generics.CreateAPIView):
    serializer_class = PluginInstallWithZIPURLSerializer

    def perform_create(self, serializer):
        zip_url = serializer.validated_data['zip_url']
        plugin_type = serializer.validated_data['plugin_type']
        
        # Download the ZIP file
        response = requests.get(zip_url, stream=True)
        if response.status_code != 200:
            raise ValidationError({'zip_url': 'Failed to download the ZIP file.'})
        
        # Save the ZIP file temporarily
        with tempfile.TemporaryDirectory() as tmpdirname:
            temp_zip_path = os.path.join(tmpdirname, 'plugin.zip')
            with open(temp_zip_path, 'wb') as temp_zip_file:
                for chunk in response.iter_content(chunk_size=128):
                    temp_zip_file.write(chunk)

            # Extract the ZIP file
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdirname)

            # Determine the plugin name and target directory
            plugin_name = os.path.basename(zip_url).rsplit('.', 1)[0]
            source_dir = os.path.join(tmpdirname, plugin_name)
            target_dir = os.path.join(get_module_path(PLUGIN_BASE_DIR), plugin_name)

            # Move the extracted files to the target directory
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.move(source_dir, target_dir)

            # Install requirements if requirements.txt exists
            requirements_path = os.path.join(target_dir, 'requirements.txt')
            if os.path.exists(requirements_path):
                subprocess.run(['pip', 'install', '-r', requirements_path], check=True)
            
            # Create or update the plugin record in the database
            Plugin.objects.update_or_create(
                name=plugin_name,
                defaults={
                    'description': '',
                    'path': target_dir,
                    'plugin_type': plugin_type,
                    'is_active': True,
                    'home_url': zip_url,
                    'documentation_url': zip_url
                }
            )

        return Response(
            {'message': 'Plugin downloaded, extracted, and registered successfully'},
            status=status.HTTP_201_CREATED,
        )