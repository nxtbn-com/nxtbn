from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import HttpRequest


class CustomAccountAdapter(DefaultAccountAdapter):
    pass


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    pass