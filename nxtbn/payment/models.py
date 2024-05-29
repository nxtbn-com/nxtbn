from datetime import timezone
from django.db import models

from nxtbn.core import CurrencyTypes, MoneyFieldTypes
from nxtbn.core.mixin import MonetaryMixin
from nxtbn.core.models import  AbstractBaseUUIDModel
from nxtbn.order import OrderStatus
from nxtbn.order.models import Order
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError


from nxtbn.payment import PaymentMethod, PaymentStatus
from nxtbn.payment.payment_manager import PaymentManager
from nxtbn.payment.utils import get_plugin_list
from nxtbn.users.admin import User

class Payment(MonetaryMixin, AbstractBaseUUIDModel):
    money_validator_map = {
        "payment_amount": {
            "currency_field": "currency",
            "type": MoneyFieldTypes.SUBUNIT,
        },
    }
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="+")
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)

    # For storing payment gateway references
    transaction_id = models.CharField(max_length=100, blank=True, null=True, unique=True)  
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.AUTHORIZED)

    currency = models.CharField(
        max_length=3,
        default=CurrencyTypes.USD,
        choices=CurrencyTypes.choices,
    )
    payment_amount = models.BigIntegerField(validators=[MinValueValidator(1)])

    gateway_response_raw = models.JSONField(null=True, blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    """
        The `payment_plugin_id` field indicates which payment gateway is used. It must match a directory 
        in nxtbn.payment.plugins. payment getway dirctory may comes with suffic or prefix, the payment get id is considred directory name.

        If the value doesn't match a directory in `nxtbn.payment.plugins`, it raises a ValidationError.
    """
    payment_plugin_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_name = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.validate_amount()
        super(Payment, self).save(*args, **kwargs)

    def authorize_payment(self, amount: Decimal, **kwargs): # TO DO: Do we still need this method?
        """Authorize payment through the specified gateway."""
        manager = PaymentManager(self.payment_plugin_id)
        response = manager.authorize_payment(amount, str(self.order.id))
        # Update model fields based on the response
        if response:
            self.transaction_id = response.transaction_id
            if response.raw_data:
                self.gateway_response_raw = response.raw_data
            self.payment_status = PaymentStatus.AUTHORIZED
            self.save()
        return response

    def capture_payment(self, amount: Decimal): # TO DO: Do we still need this method?
        """Capture authorized payment."""
        manager = PaymentManager(self.payment_plugin_id)
        response = manager.capture_payment(amount, str(self.order.id))
        if response:
            self.payment_status = PaymentStatus.CAPTURED
            self.paid_at = timezone.now()
            if response.raw_data:
                self.gateway_response_raw = response.raw_data
            self.save()
        return response

    def cancel_payment(self):
        """Cancel authorized payment."""
        manager = PaymentManager(self.payment_plugin_id)
        response = manager.cancel_payment(str(self.order.id))
        if response:
            self.payment_status = PaymentStatus.CANCELED
            if response.raw_data:
                self.gateway_response_raw = response.raw_data
            self.save()
        return response

    def refund_payment(self, amount: Decimal):
        """Refund captured payment."""
        if not self.order.status == OrderStatus.RETURNED:
            raise ValidationError("Cannot refund payment for an order that is not returned.")

        if amount > self.payment_amount:
            raise ValidationError("Refund amount cannot exceed the paid amount.")

        manager = PaymentManager(self.payment_plugin_id)
        response = manager.refund_payment(self.pk, amount)

        if response:
            self.payment_status = PaymentStatus.REFUNDED
            if response.raw_data:
                self.gateway_response_raw = response.raw_data
            self.save()
        return response

    def clean(self):
        super().clean()
        valid_gateways = get_plugin_list()
        if self.payment_plugin_id and self.payment_plugin_id not in valid_gateways:
            raise ValidationError(
                f"Invalid payment gateway: '{self.payment_plugin_id}'. "
                f"Allowed gateways are: {', '.join(valid_gateways)}."
            )





class PaymentSource(AbstractBaseUUIDModel):
    """
    Model to store customer's payment methods across multiple payment gateways.

    This model captures and stores details of various payment methods associated with a user.
    It supports multiple payment gateways by storing gateway-specific identifiers and allows 
    for easy integration with different payment processing systems.

    The purpose of this model is to store user payment method information securely so that users 
    do not need to re-enter their payment details for future purchases. By storing this information,
    users can make payments with a single click, enhancing the convenience and efficiency of the 
    checkout process.

    Fields:
        user (ForeignKey): A reference to the User model, linking the payment method to a specific user. 
            It allows null and blank values to handle cases where the user might not be immediately known.
        gateway_customer_id (CharField): The customer ID assigned by the payment gateway. 
            This is used to reference the customer in the gateway's system.
        gateway_payment_method_id (CharField): The payment method ID assigned by the payment gateway. 
            This is used to reference the payment method in the gateway's system.
        is_default (BooleanField): A flag indicating whether this payment method is the default for the user. 
            Only one payment method per user should have this flag set to True.
        payment_plugin_id (CharField): An identifier for the payment plugin used. 
            This helps in distinguishing between different payment plugins if multiple are used in the system.
        gateway_name (CharField): The name of the payment gateway (e.g., 'stripe', '2checkout', 'square'). 
            This helps in identifying the gateway associated with this payment method.
        
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="+")
    gateway_customer_id = models.CharField(max_length=255, null=True, blank=True)
    gateway_payment_method_id = models.CharField(max_length=255, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    payment_plugin_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_name = models.CharField(max_length=100, blank=True, null=True)

    # Card details
    card_last4 = models.CharField(_("Last 4 Digits"), max_length=4, null=True, blank=True)
    card_exp_month = models.CharField(_("Expiry Month"), max_length=2, null=True, blank=True)
    card_exp_year = models.CharField(_("Expiry Year"), max_length=4, null=True, blank=True)
    card_brand = models.CharField(_("Card Brand"), max_length=20, null=True, blank=True)