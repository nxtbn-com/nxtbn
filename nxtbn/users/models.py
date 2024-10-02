from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from nxtbn.users import UserRole

class User(AbstractUser):
    role = models.CharField(max_length=255, choices=UserRole.choices, default=UserRole.CUSTOMER)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
