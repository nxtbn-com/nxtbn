from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from nxtbn.core.models import AbstractBaseModel
from nxtbn.discount import PromoCodeType

class PromoCode(AbstractBaseModel):
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    code_type = models.CharField(
        max_length=20,
        choices=PromoCodeType.choices,
        default=PromoCodeType.PERCENTAGE,
    )
    value = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., 10 for 10%, or 10 for $10
    expiration_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Ensure the code is in uppercase
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def is_valid(self):
        return self.active and (self.expiration_date is None or self.expiration_date > timezone.now())