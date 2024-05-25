import importlib
from django.conf import settings


if settings.CURRENCY_BACKEND:
    currency_Backend = importlib.import_module(settings.CURRENCY_BACKEND) # Import the currency backend module specified in settings