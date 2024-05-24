from django.db import models
from django.utils.translation import gettext_lazy as _



class PromoCodeType(models.TextChoices):
    PERCENTAGE = 'PERCENTAGE', _('Percentage')
    FIXED_AMOUNT = 'FIXED', _('Fixed Amount')