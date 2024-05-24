from django.db import models
from nxtbn.core.models import AbstractBaseModel

class Vendor(AbstractBaseModel):
    name = models.CharField(max_length=100)
    contact_info = models.TextField(blank=True)
