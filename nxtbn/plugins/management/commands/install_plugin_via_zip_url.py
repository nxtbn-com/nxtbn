# myapp/management/commands/install_plugin_from_zip.py

import os
import tempfile
import requests

from django.core.management.base import BaseCommand, CommandError
from nxtbn.plugins.utils import PluginHandler

class Command(BaseCommand):
    help = 'Install plugin from a ZIP URL'

    def add_arguments(self, parser):
        parser.add_argument('zip_url', type=str, help='The URL of the ZIP file to install the plugin from')

    def handle(self, *args, **options):
        zip_url = options['zip_url']
        response = requests.get(zip_url, stream=True)
        if response.status_code != 200:
            raise CommandError('Failed to download the ZIP file.')

        handler = PluginHandler()

        with tempfile.TemporaryDirectory() as tmpdirname:
            temp_zip_path = os.path.join(tmpdirname, 'plugin.zip')
            with open(temp_zip_path, 'wb') as temp_zip_file:
                for chunk in response.iter_content(chunk_size=128):
                    temp_zip_file.write(chunk)
            handler.handle_uploaded_file(temp_zip_path)

        self.stdout.write(self.style.SUCCESS('Plugin downloaded, extracted, and registered successfully'))
