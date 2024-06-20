from django.contrib import admin

from nxtbn.plugins.models import Plugin

@admin.register(Plugin)
class PluginAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'plugin_type', 'is_active', 'is_default', 'home_url', 'documentation_url')
    list_filter = ('plugin_type', 'is_active', 'is_default')
    search_fields = ('name', 'description', 'tag')
    # readonly_fields = ('path',)