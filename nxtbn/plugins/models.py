from django.conf import settings
from django.db import models
import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from nxtbn.core.models import AbstractBaseModel
from nxtbn.plugins import PluginType
from nxtbn.core.utils import make_path

def validate_plugin_name(value):
    if not re.match(r'^[a-z0-9_]+$', value):
        raise ValidationError(
            _('Name can only contain lowercase letters, numbers, and underscores.')
        )


fixed_dirs = {
    PluginType.CURRENCY_BACKEND: 'currency_backend',
    PluginType.SMS_SERVICE: 'sms_service',
    PluginType.EMAIL_SERVICE: 'email_service',
}


class Plugin(AbstractBaseModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        primary_key=True,
        validators=[validate_plugin_name]
    )
    description = models.TextField(null=True, blank=True)
    path = models.FilePathField(allow_folders=True, path=make_path(settings.PLUGIN_BASE_DIR))
    plugin_type = models.CharField(
        max_length=20,
        choices=PluginType.choices,
        default=PluginType.GENERAL,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    has_deleted = models.BooleanField(default=False)
    home_url = models.URLField(null=True, blank=True)
    documentation_url = models.URLField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'plugin_type')
        ordering = ('name',)

    def clean(self):
        super().clean()
        # Derive the unique plugin types from the predefined folders
        unique_plugin_types = fixed_dirs.keys()

        if self.plugin_type in unique_plugin_types and self.is_active:
            existing_active_plugins = Plugin.objects.filter(
                plugin_type=self.plugin_type,
                is_active=True,
                has_deleted=False
            ).exclude(pk=self.pk)
            if existing_active_plugins.exists():
                raise ValidationError(f"There can only be one active plugin for {self.plugin_type}.")

        # Ensure the path is set correctly for predefined plugin types
        predefined_folder = fixed_dirs.get(self.plugin_type, '')
        if predefined_folder:
            expected_path = make_path(f"{settings.PLUGIN_BASE_DIR}/{predefined_folder}")
            if self.path != expected_path:
                raise ValidationError(f"The path for {self.plugin_type.label} must be {expected_path}.")

    def __str__(self):
        return self.name
    
    def to_dotted_path(self):
        """Convert path from slash notation to dot notation."""
        return self.path.replace('/', '.')