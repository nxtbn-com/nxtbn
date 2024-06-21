from django.conf import settings
from django.core.cache import caches
from nxtbn.plugins.models import Plugin
import shutil
import os

class PluginPathManager:
    DEFAULT_CACHE_TIMEOUT = 7 * 24 * 60 * 60  # Cache for one week

    def __init__(self, plugin_name, plugin_type):
        self.plugin_name = plugin_name
        self.plugin_type = plugin_type
        self.cache_key = f"{plugin_type}_plugin_path_{plugin_name}"
        self.cache_backend = 'memcached_for_plugins'  # Use Memcached for plugins

    def get_plugin(self):
        """Fetch the plugin object from the database."""
        try:
            return Plugin.objects.get(name=self.plugin_name, is_active=True, plugin_type=self.plugin_type)
        except Plugin.DoesNotExist:
            return None

    def get_plugin_path(self):
        """Get the full path to the directory for the given plugin."""
        cache = caches[self.cache_backend]
        path = cache.get(self.cache_key)
        if not path:
            plugin = self.get_plugin()
            if plugin:
                path = plugin.to_dotted_path()
                cache.set(self.cache_key, path, timeout=self.DEFAULT_CACHE_TIMEOUT)
            else:
                return None
        return path

    @classmethod
    def get_plugin_path(cls, plugin_name, plugin_type):
        manager = cls(plugin_name, plugin_type)
        return manager.get_plugin_path()

    def cache_plugin_path(self, plugin):
        """Cache the plugin path."""
        if plugin.is_active:
            cache = caches[self.cache_backend]
            path = plugin.to_dotted_path()
            cache.set(self.cache_key, path, timeout=self.DEFAULT_CACHE_TIMEOUT)
        else:
            self.remove_plugin_from_cache(plugin)

    @classmethod
    def cache_plugin_path(cls, plugin):
        manager = cls(plugin.name, plugin.plugin_type)
        manager.cache_plugin_path(plugin)

    def remove_plugin_from_cache(self, plugin):
        """Remove the plugin path from cache."""
        cache = caches[self.cache_backend]
        cache.delete(self.cache_key)

    @classmethod
    def remove_plugin_from_cache(cls, plugin):
        manager = cls(plugin.name, plugin.plugin_type)
        manager.remove_plugin_from_cache(plugin)

    def check_plugin_path(self):
        """Check if the plugin path exists in the cache, and query if not found in cache."""
        if self.get_plugin_path():
            return True
        return False

    @classmethod
    def check_plugin_path(cls, plugin_name, plugin_type):
        manager = cls(plugin_name, plugin_type)
        return manager.check_plugin_path()

    def remove_plugins(self):
        """Remove the plugin directory and its path from cache."""
        cache = caches[self.cache_backend]
        path = cache.get(self.cache_key)
        if path and os.path.isdir(path):
            shutil.rmtree(path)  # Remove the directory and all its contents

        plugin = self.get_plugin()
        if plugin:
            self.remove_plugin_from_cache(plugin)

    @classmethod
    def remove_plugins(cls, plugin_name, plugin_type):
        manager = cls(plugin_name, plugin_type)
        manager.remove_plugins()
