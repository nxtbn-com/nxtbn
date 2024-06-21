import importlib
import os
import zipfile
import shutil
import subprocess
import tempfile
import logging

from django.conf import settings
from django.forms import ValidationError
from packaging.version import parse as parse_version
from packaging.specifiers import SpecifierSet

from nxtbn.plugins.models import Plugin, fixed_dirs

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


class PluginHandler:
    def __init__(self):
        self.tmpdirname = tempfile.mkdtemp()

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

        plugin_type = plugin_metadata.get('plugin_type')
        if fixed_dirs.get(plugin_type, ''):
            plugin_name = fixed_dirs.get(plugin_type)
        else:
            plugin_name = plugin_metadata.get('plugin_name')

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
