import os
import logging
import shutil

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.forms import ValidationError
from packaging.version import parse as parse_version
from packaging.specifiers import SpecifierSet

from nxtbn.plugins.models import Plugin, fixed_dirs
from nxtbn.plugins.utils import extract_metadata, get_module_path

logger = logging.getLogger(__name__)

PLUGIN_BASE_DIR = getattr(settings, 'PLUGIN_BASE_DIR')

class Command(BaseCommand):
    help = 'Register manually placed plugins in the plugin directory'

    def add_arguments(self, parser):
        parser.add_argument('plugin_name', type=str, help='The name of the plugin to register')

    def handle(self, *args, **options):
        plugin_name = options['plugin_name']
        plugin_dir = os.path.join(get_module_path(PLUGIN_BASE_DIR), plugin_name)

        if not os.path.exists(plugin_dir):
            raise CommandError(f"Plugin directory '{plugin_dir}' does not exist.")

        init_file_path = os.path.join(plugin_dir, '__init__.py')
        if not os.path.exists(init_file_path):
            raise CommandError(f"__init__.py file not found in the plugin directory '{plugin_dir}'.")

        plugin_metadata = extract_metadata(init_file_path)

        plugin_type = plugin_metadata.get('plugin_type')
        nxtbn_version_compatibility = plugin_metadata.get('nxtbn_version_compatibility')

        if not plugin_name or not plugin_type:
            raise CommandError('Plugin name or type not found in metadata.')

        if nxtbn_version_compatibility:
            current_version = parse_version(settings.VERSION)
            specifier = SpecifierSet(nxtbn_version_compatibility)
            if not current_version in specifier:
                raise CommandError(f"Plugin version {nxtbn_version_compatibility} is not compatible with the current version {settings.VERSION}.")

        relative_path = os.path.relpath(plugin_dir, start=settings.BASE_DIR)

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

        self.stdout.write(self.style.SUCCESS(f"Plugin '{plugin_name}' registered successfully"))
