import importlib
from django.conf import settings



currency_Backend = importlib.import_module(settings.CURRENCY_BACKEND).currency_Backend