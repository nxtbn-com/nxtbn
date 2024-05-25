from nxtbn.core.currency import currency_Backend
from babel.numbers import format_currency



def convert_to_currency(subunit_price):
    exchange_rate = CurrencyExchange.get_exchange_rate()  # Get the exchange rate from your currency backend
    amount = subunit_price / 100
    converted_amount = amount / exchange_rate
    formatted_amount = format_currency(converted_amount, 'USD', locale='en_US')  # Replace 'USD' with your desired currency code
    return formatted_amount