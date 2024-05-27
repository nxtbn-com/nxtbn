import importlib
from django.conf import settings


if settings.CURRENCY_BACKEND:
    currency_Backend = importlib.import_module(settings.CURRENCY_BACKEND).currency_Backend
else:
    # Fallback to default backend if CURRENCY_BACKEND is not set,
    # but note that it may not function as expected without proper configuration.
    # you will get TypeError: Can't instantiate abstract class CurrencyBackend with abstract method fetch_data, the error is expected
    from nxtbn.core.currency.abstract_base_currency import CurrencyBackend as currency_Backend