from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from nxtbn.plugins.manager import PluginPathManager
from nxtbn.plugins.models import Plugin


@receiver(post_save, sender=Plugin)
def handle_plugin_save(sender, instance, **kwargs):
    PluginPathManager.cache_plugin_path(instance)

@receiver(post_delete, sender=Plugin)
def handle_plugin_delete(sender, instance, **kwargs):
    PluginPathManager.remove_plugin_from_cache(instance)