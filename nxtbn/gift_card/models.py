from django.db import models
from django.utils import timezone

from nxtbn.users.admin import User

from nxtbn.core.models import AbstractBaseModel

class GiftCard(AbstractBaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='gift_cards')
    code = models.CharField(max_length=20, unique=True)
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2)  # initial amount in dollars
    current_balance = models.DecimalField(max_digits=10, decimal_places=2)  # remaining balance
    expiration_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def is_valid(self):
        return self.active and (self.expiration_date is None or self.expiration_date > timezone.now())

    def __str__(self):
        return f"{self.code} - {self.current_balance}"