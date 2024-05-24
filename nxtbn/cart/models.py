from django.db import models

from django.core.validators import MinValueValidator
from decimal import Decimal

from nxtbn.core.models import AbstractBaseModel, AbstractBaseUUIDModel
from nxtbn.product.models import ProductVariant
from nxtbn.users.models import User   


class CartItem(AbstractBaseUUIDModel):
    """
        Represents a shopping cart within the system, allowing users to gather items for future purchase.

        Cart Mechanism Overview:

        This cart system is designed to cater to both authenticated and unauthenticated users:

        For Unauthenticated Users:
        - Unauthenticated users can add items to their cart, and this data is stored locally in cookies/localStorage.
        - They have the ability to proceed to checkout by providing minimal information such as email, phone number, and address.
        - Upon successful order placement, cart items stored in cookies/localStorage are automatically cleared, resetting the cart.

        For Authenticated Users:
        - Users adding items to the cart while not logged in will have their cart items synchronized upon authentication.
        - The system prioritizes backend data integrity over local cookies/localStorage, ensuring consistency.
        - If discrepancies arise between the backend and cookies/localStorage, the backend data supersedes and updates the local cart.
        - Upon successful order placement, the cart items are removed from the database and the local cookies/localStorage, providing a seamless experience.

        Delete Flow:
        - If an authenticated user successfully places an order, the corresponding cart items are removed from the database and synced with the local cookies/localStorage.
        - For unauthenticated users, upon reaching the success screen after order placement, the cart is reset, clearing any stored items.

        Key Features:
        - Seamless transition from anonymous to authenticated status with cart persistence.
        - Backend-backend synchronization to maintain accurate cart data.
        - Graceful handling of user actions, providing a seamless shopping experience.
    """

    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name='cart_items'
    )
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.product_variant.name} in Cart {self.cart.id}"
