import importlib
from django.conf import settings
from babel.numbers import get_currency_precision, format_currency
from nxtbn.core.models import CurrencyExchange



def convert_to_target_currency(target_currency: str, amount: float) -> float:
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
            base_currency=settings.BASE_CURRENCY,
            target_currency=target_currency
        ).exchange_rate
        converted_amount = amount * exchange_rate
        formatted_amount = format_currency(converted_amount, target_currency, locale='en_US', format_type='standard')
        return formatted_amount
    except CurrencyExchange.DoesNotExist:
        raise ValueError(f"Exchange rate for {target_currency} not found.")