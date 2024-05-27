from django.db import models

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from nxtbn.core import CurrencyTypes, MoneyFieldTypes
from nxtbn.core.mixin import MonetaryMixin
from nxtbn.core.models import AbstractAddressModels, AbstractBaseModel, AbstractBaseUUIDModel
from nxtbn.discount.models import PromoCode
from nxtbn.gift_card.models import GiftCard
from nxtbn.order import OrderAuthorizationStatus, OrderChargeStatus, OrderStatus
from nxtbn.payment import PaymentMethod
from nxtbn.product.models import ProductVariant
from nxtbn.users.admin import User
from nxtbn.vendor.models import Vendor

from money.money import Currency, Money
from babel.numbers import get_currency_precision, format_currency


class Address(AbstractAddressModels):

    # Customizable Receiver Information / may redundent with user
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)
    is_default_delivery_address = models.BooleanField(default=False)

    class Meta:
        ordering = ('-is_default_delivery_address', 'last_name', 'first_name')

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.street_address}, {self.city}, {self.country}"

class Order(MonetaryMixin, AbstractBaseUUIDModel):
    """
    Represents an order placed by a customer.

    An order consists of one or more items purchased by the customer.
    It tracks the status of the order, payment details, and shipping information.

    Attributes:
        order_number (str): A unique identifier for the order.
        customer (ForeignKey): The customer who placed the order.
        total_amount (Decimal): The total amount of the order.
        authorization_status (OrderAuthorizationStatus): The authorization status of the order's funds.
        charge_status (OrderChargeStatus): The charge status of the order's transaction charges.
        status (OrderStatus): The current status of the order's lifecycle.
        created_at (datetime): The date and time when the order was created.
        last_modified (datetime): The date and time when the order was last updated.

    Note:
        - The `authorization_status` field indicates whether funds have been authorized for the order,
          and to what extent they cover the order's total amount.
        - The `charge_status` field indicates whether funds have been charged for the order,
          and to what extent they cover the order's total amount.
        - The `status` field tracks the different stages of the order's lifecycle,
          such as pending, processing, shipped, delivered, cancelled, or returned.
    """

    # https://docs.nxtbn.com/moneyvalidation
    money_validator_map = {
        "total_price": {
            "currency_field": "currency",
            "type": MoneyFieldTypes.SUBUNIT,
            "require_base_currency": True,
        },
        "total_price_in_customer_currency": {
            "currency_field": "customer_currency",
            "type": MoneyFieldTypes.UNIT,
        },
    }



    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders", null=True, blank=True)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    shipping_address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL, related_name="shipping_orders")
    billing_address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL, related_name="billing_orders")


    currency = models.CharField(
        max_length=3,
        default=CurrencyTypes.USD,
        choices=CurrencyTypes.choices,
        help_text="ISO currency code for the order. This is the base currency in which the total amount will be stored after converting from the customer's currency to the base currency. "
                "For example, 'USD' for US Dollars. The base currency is defined in the settings."
    )
    total_price = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1)],
        help_text="Total amount of the order in cents, converted from the original currency (customer's currency) to the base currency. "
                "For example, if the base currency is USD and the customer_currency is different (e.g., AUD), the total amount will be converted to USD. "
                "This converted amount is stored in cents."
    )
    customer_currency = models.CharField(
        max_length=3,
        default=CurrencyTypes.USD,
        choices=CurrencyTypes.choices,
        help_text="ISO currency code of the original amount paid by the customer. "
                "For example, 'AUD' for Australian Dollars."
    )
    total_price_in_customer_currency = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=4,
        max_digits=12,
        help_text="Original amount paid by the customer in the customer's currency, stored in cents. "
    )


    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        help_text="Represents the current stage of the order within its lifecycle.",
        verbose_name="Order Status",
    )
    authorize_status = models.CharField(
        max_length=32,
        default=OrderAuthorizationStatus.NONE,
        choices=OrderAuthorizationStatus.choices,
        help_text="Represents the authorization status of the order based on fund coverage.",
        verbose_name="Authorization Status",
    )
    charge_status = models.CharField(
        max_length=32,
        default=OrderChargeStatus.NONE,
        choices=OrderChargeStatus.choices,
        help_text="Represents the charge status of the order based on transaction charges.",
        verbose_name="Charge Status",
    )

    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)
    gift_card = models.ForeignKey(GiftCard, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',) # # Most recent orders first

    def save(self, *args, **kwargs):
        self.validate_amount()
        super(Order, self).save(*args, **kwargs)

    def apply_promo_code(self): # TODO: Do we still need this?
        """
        Apply a promotional code to the order, reducing the total price accordingly.

        If the promo code is valid and active, the discount is calculated based on the type
        of promo code (either a percentage or a fixed amount). The order's total is reduced
        by the calculated discount.

        This method does not automatically save the changes to the database. You must call
        `order.save()` after calling this method to persist changes.

        Returns:
            decimal.Decimal: The amount of the discount applied to the order, or 0 if no discount is applied.
    """
        if self.promo_code and self.promo_code.is_valid():
            if self.promo_code.code_type == 'percentage':
                discount = (self.total * (self.promo_code.value / 100))
            else:
                discount = self.promo_code.value
            self.total -= discount
            return discount
        return 0

    def apply_gift_card(self):  # TODO Do we still need this?
        """
            Apply a gift card to the order, reducing the total price by the balance available on the gift card.

            If the gift card is valid and has sufficient balance, the order's total will be reduced accordingly.
            If the gift card's balance is greater than or equal to the order's total, the order's total is set to
            zero. Otherwise, the order's total is reduced by the gift card's balance.

            This method does not automatically save the changes to the database. You must call `order.save()`
            after calling this method to persist changes.

            Note:
                This method reduces the gift card's balance according to the applied discount.

            Returns:
                None
        """
        if self.gift_card and self.gift_card.is_valid():
            if self.gift_card.current_balance >= self.total:
                self.gift_card.reduce_balance(self.total)
                self.total = 0
            else:
                self.total -= self.gift_card.current_balance
                self.gift_card.reduce_balance(self.gift_card.current_balance)
    

    def total_in_units(self): #subunit -to-unit 
        precision = get_currency_precision(self.currency)
        unit = self.total_price / (10 ** precision)
        return unit
    
    def humanize_total_price(self):
        """
        Returns the total price of the order formatted with the currency symbol,
        making it more human-readable.

        Returns:
            str: The formatted total price with the currency symbol.
        """
        return format_currency(self.total_in_units(), self.currency, locale='en_US')
    
    def __str__(self):
        return f"Order {self.id} - {self.status}"


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="line_items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="+")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal("0.01"))])
    total_price = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal("0.01"))])

    def __str__(self):
        return f"{self.variant.product.name} - {self.variant.name} - Qty: {self.quantity}"

