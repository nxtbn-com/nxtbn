import importlib
import os
import zipfile
import shutil
import subprocess

from django.conf import settings
import tempfile

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
from nxtbn.core.api.dashboard.serializers import PluginInstallSerializer, ZipFileUploadSerializer

PLUGIN_DIR = getattr(settings, 'PLUGIN_DIR')
PAYMENT_PLUGIN_DIR =  getattr(settings, 'PAYMENT_PLUGIN_DIR')

os.makedirs(PLUGIN_DIR, exist_ok=True)

def get_module_path(module_name):
    spec = importlib.util.find_spec(module_name)
    if spec and spec.origin:
        return os.path.dirname(spec.origin)
    raise ImportError(f"Module {module_name} not found")

class PlugginsInstallViaGitView(generics.CreateAPIView):
    "upload plugin via repository url, example url: https://[github/bitbucket/gitlab].com/nxtbn-com/stripe-payment-link"
    serializer_class = PluginInstallSerializer

    def perform_create(self, serializer):
        git_url = serializer.validated_data['git_url']
        plugin_type = serializer.validated_data['plugin_type']
        
        # Determine the target directory based on the plugin type
        if plugin_type == PluginType.PAYMENT_PROCESSOR:
            target_dir_base =  get_module_path(PAYMENT_PLUGIN_DIR)
        else:
            target_dir_base = get_module_path(PLUGIN_DIR)
        
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

        return Response(
            {'message': 'Plugin cloned, .git removed, and requirements installed successfully'},
            status=status.HTTP_201_CREATED,
        )


class PlugginsUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ZipFileUploadSerializer(data=request.data)

        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']

            storage = FileSystemStorage(location=PLUGIN_DIR)
            file_path = storage.save(uploaded_file.name, uploaded_file)

            full_file_path = os.path.join(PLUGIN_DIR, uploaded_file.name)
            with zipfile.ZipFile(full_file_path, 'r') as zip_ref:
                zip_ref.extractall(PLUGIN_DIR)

            return Response(
                {'message': 'ZIP file uploaded and extracted successfully'},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


