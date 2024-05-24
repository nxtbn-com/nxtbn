from django.db.models.signals import post_migrate
from django.dispatch import receiver
from nxtbn.core.models import SiteSettings

@receiver(post_migrate)
def create_default_site_settings(sender, **kwargs):
    if SiteSettings.objects.count() == 0:
        SiteSettings.objects.create(site_name="nxtbn commerce")
