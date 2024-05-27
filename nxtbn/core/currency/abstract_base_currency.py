from abc import ABC, abstractmethod
from typing import Dict, List
from django.conf import settings
from nxtbn.core.models import CurrencyExchange

from babel.numbers import get_currency_precision, format_currency

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

    def refresh_rate(self):
        for fetch_data in self.fetch_data():
            CurrencyExchange.objects.update_or_create(
                base_currency=self.base_currency,
                target_currency=fetch_data['target_currency'],
                defaults={'exchange_rate': fetch_data['exchange_rate']}
            )

    def convert_to_target_currency(self, target_currency: str, amount: float) -> float:
        """
        Convert the given amount from the base currency to the target currency,
        considering the currency precision.
        
        Args:
        - target_currency: str
        - amount: float
        
        Returns:
        - float: Amount in the target currency, formatted to the correct precision.
        """
        try:
            exchange_rate = CurrencyExchange.objects.get(
                base_currency=self.base_currency,
                target_currency=target_currency
            ).exchange_rate
            converted_amount = amount * exchange_rate
            precision = get_currency_precision(target_currency)
            formatted_amount = format_currency(converted_amount, target_currency, locale='en_US', format_type='standard')
            return formatted_amount
        except CurrencyExchange.DoesNotExist:
            raise ValueError(f"Exchange rate for {target_currency} not found.")