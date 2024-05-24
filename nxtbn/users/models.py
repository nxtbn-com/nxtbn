from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
