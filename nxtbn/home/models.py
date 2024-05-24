from django.db import models

class MetaGlobal(models.Model):
    regular_menu = models.JSONField()
    mega_menu = models.JSONField()

    uncategorized_footer = models.JSONField()
    categorized_footer = models.JSONField()
    logo = models.ImageField()
    
    metadata = models.JSONField()


