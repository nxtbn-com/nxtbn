from django.core.cache import cache
from nxtbn.plugins.models import Plugin

class PluginPathManager:
    DEFAULT_CACHE_TIMEOUT = 7 * 24 * 60 * 60  # Cache for one week

    def __init__(self, plugin_name, plugin_type):
        self.plugin_name = plugin_name
        self.plugin_type = plugin_type
        self.cache_key = f"{plugin_type}_plugin_path_{plugin_name}"

    @classmethod
    def get_plugin_path(cls, plugin_name, plugin_type):
        """Get the full path to the directory for the given plugin."""
        manager = cls(plugin_name, plugin_type)
        path = cache.get(manager.cache_key)

        if not path:
            try:
                plugin = Plugin.objects.get(name=plugin_name, is_active=True, plugin_type=plugin_type)
                path = plugin.to_module()
                cache.set(manager.cache_key, path, timeout=cls.DEFAULT_CACHE_TIMEOUT)
            except Plugin.DoesNotExist:
                return None

        return path

    @classmethod
    def cache_plugin_path(cls, plugin):
        """Cache the plugin path."""
        if plugin.is_active:
            manager = cls(plugin.name, plugin.plugin_type)
            path = plugin.to_module()
            cache.set(manager.cache_key, path, timeout=cls.DEFAULT_CACHE_TIMEOUT)
        else:
            cls.remove_plugin_from_cache(plugin)

    @classmethod
    def remove_plugin_from_cache(cls, plugin):
        """Remove the plugin path from cache."""
        manager = cls(plugin.name, plugin.plugin_type)
        cache.delete(manager.cache_key)

    @classmethod
    def check_plugin_path(cls, plugin_name, plugin_type):
        """Check if the plugin path exists in the cache, and query if not found in cache."""
        manager = cls(plugin_name, plugin_type)
        path = cache.get(manager.cache_key)

        if path:
            return True

        try:
            plugin = Plugin.objects.get(name=plugin_name, is_active=True, plugin_type=plugin_type)
            path = plugin.to_module()
            cache.set(manager.cache_key, path, timeout=cls.DEFAULT_CACHE_TIMEOUT)
            return True
        except Plugin.DoesNotExist:
            return False
