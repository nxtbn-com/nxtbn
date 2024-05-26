from django.conf import settings
from django.core.exceptions import ValidationError
from money.money import Currency, Money
from decimal import InvalidOperation
from money.exceptions import InvalidAmountError, CurrencyMismatchError
from typing import TypedDict

from nxtbn.core import MoneyFieldTypes




class MoneyFieldConfiguration(TypedDict):
    """Type definition for configuring money fields with their related currency fields."""
    amount_type: MoneyFieldTypes
    currency_field_name: str
    require_base_currency: bool

class MonetaryMixin:
    """
    Mixin for validating currency-related fields in Django models.
    
    Attributes:
        money_validator_map (dict): A dictionary mapping field names to their configurations.
    """
    money_validator_map: 'dict[str, dict]' = {}

    def validate_amount(self):
        """
        Automatically validates all monetary fields specified in the money_validator_map dictionary.
        No arguments are needed as it uses the internal money_validator_map for configuration.
        """
        for field_name, config in self.money_validator_map.items():
            amount = getattr(self, field_name)
            if amount is None:
                continue  # Skip validation if the amount is None

            currency_str = getattr(self, config["currency_field"])
            try:
                currency = Currency(currency_str)
            except ValueError:
                raise ValidationError({field_name: f"Invalid currency '{currency_str}'"})

            try:
                if config["type"] == MoneyFieldTypes.UNIT:
                    Money(amount, currency)
                elif config["type"] == MoneyFieldTypes.SUBUNIT:
                    Money.from_sub_units(amount, currency)
            except (InvalidAmountError, InvalidOperation):
                raise ValidationError({field_name: f"Invalid amount '{amount}' for currency '{currency_str}'"})
            
            if config.get("require_base_currency", False):
                if currency_str != settings.BASE_CURRENCY:
                    raise ValidationError({field_name: f"Currency field '{field_name}' expects value same as base currency '{settings.BASE_CURRENCY}', other currency values can't be added"})