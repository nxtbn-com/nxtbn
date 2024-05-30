from babel.numbers import get_currency_precision
from decimal import Decimal, ROUND_HALF_UP

def normalize_amount_currencywise(amount: float, currency_code: str):
    """    
    Warning:
    This method rounds the amount to the nearest precision defined by the currency,
    which may lead to minor value reductions. It is primarily intended for generating
    test data, management commands, or sanitizing payloads in serializers.
    
    If used outside of test case/unit testing and test data generation, 
    it should be based on merchant requirements.
    
    Parameters:
    - amount (float): The monetary amount to be formatted.
    - currency_code (str): The ISO 4217 currency code (e.g., 'USD', 'JPY', 'KWD').

    Returns:
    - int, float, or Decimal: The formatted amount with the appropriate precision.
    """
    precision = get_currency_precision(currency_code)
    amount_decimal = Decimal(str(amount))
    quantize_format = '1.' + '0' * precision
    formatted_amount = amount_decimal.quantize(Decimal(quantize_format), rounding=ROUND_HALF_UP)

    if precision == 0:
        return int(formatted_amount)
    elif precision <= 2:
        return float(formatted_amount)
    else:
        return formatted_amount