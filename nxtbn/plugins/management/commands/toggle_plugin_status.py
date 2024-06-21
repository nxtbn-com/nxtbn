from django.core.management.base import BaseCommand, CommandError
from nxtbn.plugins.models import Plugin

class Command(BaseCommand):
    help = 'Activate or deactivate a plugin'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, choices=['activate', 'deactivate'], help='Action to perform: activate or deactivate')
        parser.add_argument('plugin_name', type=str, help='The name of the plugin to activate or deactivate')

    def handle(self, *args, **options):
        action = options['action']
        plugin_name = options['plugin_name']

        try:
            plugin = Plugin.objects.get(name=plugin_name)
        except Plugin.DoesNotExist:
            raise CommandError(f"Plugin '{plugin_name}' does not exist.")

        if action == 'activate':
            plugin.is_active = True
            plugin.save()
            self.stdout.write(self.style.SUCCESS(f"Plugin '{plugin_name}' activated successfully"))
        elif action == 'deactivate':
            plugin.is_active = False
            plugin.save()
            self.stdout.write(self.style.SUCCESS(f"Plugin '{plugin_name}' deactivated successfully"))
