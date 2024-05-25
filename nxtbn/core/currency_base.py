from abc import ABC, abstractmethod
from typing import Dict, List
from django.conf import settings
from nxtbn.core.models import CurrencyExchange

class CurrencyBackend(ABC):
    def __init__(self):
        self.base_currency = settings.BASE_CURRENCY

    @abstractmethod
    def fetch_data(self) -> List[Dict[str, float]]:
        """
        Fetch exchange rate data from a remote API or data source.
        Returns a list of dictionaries, each containing:
        - target_currency: str
        - exchange_rate: float
        """
        pass

    def refresh_rate(self, data):
        for fetch_data in self.fetch_data():
            CurrencyExchange.objects.update_or_create(
                base_currency=self.base_currency,
                target_currency=fetch_data['target_currency'],
                defaults={'exchange_rate': fetch_data['exchange_rate']}
            )