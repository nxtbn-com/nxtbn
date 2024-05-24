from django.db import models
from django.utils.translation import gettext_lazy as _

class OrderAuthorizationStatus(models.TextChoices):
    """Defines the authorization status of an order based on fund coverage.

    - 'NONE': No funds are authorized.
    - 'PARTIAL': Partially authorized; authorized and charged funds do not fully cover the order's total after accounting for granted refunds.
    - 'FULL': Fully authorized; authorized and charged funds fully cover the order's total after accounting for granted refunds.
    """

    NONE = "NONE", "No funds are authorized"
    PARTIAL = "PARTIAL", "Partially authorized; funds don't fully cover the order's total"
    FULL = "FULL", "Fully authorized; funds cover the order's total"

class OrderChargeStatus(models.TextChoices):
    """Defines the charge status of an order based on transaction charges.

    - 'NONE': No funds are charged.
    - 'PARTIAL': Partially charged; charged funds don't fully cover the order's total after accounting for granted refunds.
    - 'FULL': Fully charged; charged funds fully cover the order's total after accounting for granted refunds.
    - 'OVERCHARGED': Overcharged; charged funds exceed the order's total after accounting for granted refunds.
    """

    NONE = "NONE", "No funds are charged"
    PARTIAL = "PARTIAL", "Partially charged; funds don't fully cover the order's total"
    FULL = "FULL", "Fully charged; funds cover the order's total"
    OVERCHARGED = "OVERCHARGED", "Overcharged; funds exceed the order's total"


class OrderStatus(models.TextChoices):
    """Defines the different stages of an order's lifecycle.

    - 'PENDING': Order has been placed but not yet processed.
    - 'PROCESSING': Order is being processed and prepared for shipment.
    - 'SHIPPED': Order has been shipped but not yet delivered.
    - 'DELIVERED': Order has been delivered to the customer.
    - 'CANCELLED': Order has been cancelled and will not be fulfilled.
    - 'RETURNED': Order has been returned after delivery.
    """

    PENDING = "PENDING", _("Pending")
    PROCESSING = "PROCESSING", _("Processing")
    SHIPPED = "SHIPPED", _("Shipped")
    DELIVERED = "DELIVERED", _("Delivered")
    CANCELLED = "CANCELLED", _("Cancelled")
    RETURNED = "RETURNED", _("Returned")
