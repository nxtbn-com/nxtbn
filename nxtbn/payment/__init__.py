from django.db import models
from django.utils.translation import gettext_lazy as _

class PaymentStatus(models.TextChoices):
    """Defines the different statuses of a payment process.

    - 'AUTHORIZED': Payment has been initiated but not yet completed. authorized means it is still pending
    - 'CAPTURED': Captured has been successfully completed. captured means the payment has be completed
    - 'FAILED': Payment attempt has failed or was unsuccessful.
    - 'REFUNDED': Payment has been refunded to the customer.
    - 'CANCELED': Payment has been canceled before completion.
    """

    AUTHORIZED = "AUTHORIZED", _("Authorized")
    CAPTURED = "CAPTURED", _("Captured")
    FAILED = "FAILED", _("Failed")
    REFUNDED = "REFUNDED", _("Refunded")
    CANCELED = "CANCELED", _("Canceled")



class PaymentMethod(models.TextChoices):
    """Defines different methods for processing payments.

    - 'CREDIT_CARD': Payment via credit card.
    - 'PAYPAL': Payment through PayPal.
    - 'BANK_TRANSFER': Payment via bank transfer.
    - 'CASH_ON_DELIVERY': Payment upon delivery; if not used, the order must have a linked payment instance.
    """

    CREDIT_CARD = "CREDIT_CARD", _("Credit Card")
    PAYPAL = "PAYPAL", _("PayPal")
    BANK_TRANSFER = "BANK_TRANSFER", _("Bank Transfer")
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY", _("Cash on Delivery")  # If not used, the order must have a linked payment instance.
