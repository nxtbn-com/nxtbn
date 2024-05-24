import os
import zipfile
import shutil
import subprocess

from django.conf import settings

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




from nxtbn.core.api.dashboard.serializers import URLSerializer, ZipFileUploadSerializer

PLUGIN_DIR = getattr(settings, 'PLUGIN_DIR')

os.makedirs(PLUGIN_DIR, exist_ok=True)


plugin_storage = FileSystemStorage(location=PLUGIN_DIR)

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



class UploadPaymentPlugin(generics.CreateAPIView):
    parser_class = (MultiPartParser,)
    queryset = None
    serializer_class = ZipFileUploadSerializer

    def perform_create(self, serializer):
        uploaded_file = serializer.validated_data['file']
        plugin_path = os.path.join(settings.BASE_DIR, 'nxtbn', 'payment', 'plugins')

        if uploaded_file.name.endswith('.zip'):
            try:
                with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                    zip_ref.extractall(plugin_path)
                
                os.remove(uploaded_file.name)
                
                requirement_file_path = os.path.join(plugin_path, 'requirement.txt')
                if os.path.exists(requirement_file_path):
                    subprocess.call(['pip', 'install', '-r', requirement_file_path])
                
                serializer.save()
            except Exception as e:
                raise serializers.ValidationError({'error': str(e)})
        else:
            raise serializers.ValidationError({'error': 'Uploaded file is not a ZIP file.'})

        return Response({'message': 'Files uploaded and dependencies installed successfully.'}, status=status.HTTP_200_OK)
    

class UploadInstallPaymentPlugins(generics.CreateAPIView):
    parser_classes = (JSONParser,)
    queryset = None
    serializer_class = URLSerializer

    def perform_create(self, serializer):
        zip_file_url = serializer.validated_data['url']
        plugin_path = os.path.join(settings.BASE_DIR, 'nxtbn', 'payment', 'plugins')

        try:
            response = requests.get(zip_file_url)
            if response.status_code == 200:
                with open(os.path.join(plugin_path, 'downloaded_plugins.zip'), 'wb') as f:
                    f.write(response.content)
                
                with zipfile.ZipFile(os.path.join(plugin_path, 'ddownloaded_plugins.zip'), 'r') as zip_ref:
                    zip_ref.extractall(plugin_path)
                
                os.remove(os.path.join(plugin_path, 'downloaded_plugins.zip'))
                
                requirement_file_path = os.path.join(plugin_path, 'requirement.txt')
                if os.path.exists(requirement_file_path):
                    subprocess.call(['pip', 'install', '-r', requirement_file_path])
                
                serializer.save()
            else:
                raise Exception(f"Failed to download ZIP file from URL: {zip_file_url}")

        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})

        return Response({'message': 'Files downloaded and dependencies installed successfully.'}, status=status.HTTP_200_OK)