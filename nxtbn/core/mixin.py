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

class CurrencyValidatorMixin:
    """
    Mixin for validating currency-related fields in Django models.
    
    Attributes:
        money_config (dict): A dictionary mapping field names to their configurations.
    """
    money_config: 'dict[str, dict]' = {}

    def validate_amount(self):
        """
        Automatically validates all monetary fields specified in the money_config dictionary.
        No arguments are needed as it uses the internal money_config for configuration.
        """
        for field_name, config in self.money_config.items():
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