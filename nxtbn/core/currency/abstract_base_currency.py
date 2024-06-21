from abc import ABC, abstractmethod
from typing import Dict, List
from django.conf import settings
from nxtbn.core.models import CurrencyExchange
from django.core.cache import caches
from babel.numbers import format_currency


class CurrencyBackend(ABC):
    def __init__(self):
        self.base_currency = settings.BASE_CURRENCY
        self.cache_key = f"exchange_rates_{self.base_currency}"
        self.cache_backend = 'generic'

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
        data = self.fetch_data()
        cache = caches[self.cache_backend]
        cache.set(self.cache_key, data, timeout=604800)  # Cache for 1 week

        for fetch_data in self.fetch_data():
            CurrencyExchange.objects.update_or_create(
                base_currency=self.base_currency,
                target_currency=fetch_data['target_currency'],
                defaults={'exchange_rate': fetch_data['exchange_rate']}
            )

    def get_exchange_rate(self, target_currency: str) -> float:
        cache = caches[self.cache_backend]
        cached_data = cache.get(self.cache_key)
        if cached_data:
            for rate_data in cached_data:
                if rate_data['target_currency'] == target_currency:
                    return rate_data['exchange_rate']
        
        # Fallback to database if not found in cache
        exchange_rate = CurrencyExchange.objects.filter(
            base_currency=self.base_currency,
            target_currency=target_currency
        ).values_list('exchange_rate', flat=True).first()

        try:
            exchange_rate = CurrencyExchange.objects.get(
                base_currency=settings.BASE_CURRENCY,
                target_currency=target_currency
            ).exchange_rate
            return exchange_rate
        except CurrencyExchange.DoesNotExist:
            raise ValueError(f"Exchange rate for {target_currency} not found.")


    def to_target_currency(self, target_currency: str, amount: float) -> float:
        """
        Convert the given amount from the base currency to the target currency,
        considering the currency precision.
        
        Args:
        - target_currency: str
        - amount: float
        
        Returns:
        - float: Amount in the target currency, formatted to the correct precision.
        """
        exchange_rate = self.get_exchange_rate(target_currency)
        converted_amount = amount * exchange_rate
        formatted_amount = format_currency(converted_amount, target_currency, locale='en_US', format_type='standard')
        return formatted_amount
       