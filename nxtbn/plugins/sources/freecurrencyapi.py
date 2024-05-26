from typing import Dict, List

from django.conf import settings
import requests
from nxtbn.core.currency.abstract_base_currency import CurrencyBackend
from nxtbn.settings import get_env_var

class CurrencyBackend(CurrencyBackend):
    def fetch_data(self) -> List[Dict[str, float]]:
        """
        Fetch exchange rate data from Free Currency API.
        
        Returns a list of dictionaries, each containing:
        - target_currency: str
        - exchange_rate: float
        """
        currencies = ",".join(settings.ALLOWED_CURRENCIES)
        response = requests.get(
            "https://api.freecurrencyapi.com/v1/latest",
            params={
                "apikey": get_env_var("CURRENCY_EXCHANGE_API_KEY", ""),
                "currencies": currencies,
                "base_currency": self.base_currency
            }
        )
        response_data = response.json()
        data = response_data.get('data', {})

        
        exchange_data = []
        for currency, rate in data.items():
            exchange_data.append({
                'target_currency': currency,
                'exchange_rate': rate
            })
        
        return exchange_data