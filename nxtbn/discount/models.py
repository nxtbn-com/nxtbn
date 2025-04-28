from datetime import timedelta
from django.db import models
from nxtbn.users.models import User
from django.forms import ValidationError
from django.utils import timezone

from nxtbn.core.models import AbstractBaseModel, AbstractTranslationModel
from nxtbn.discount import PromoCodeType
from nxtbn.order import OrderStatus
from nxtbn.product.models import Product


class PromoCode(AbstractBaseModel):
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    code_type = models.CharField(
        max_length=20,
        choices=PromoCodeType.choices,
        default=PromoCodeType.PERCENTAGE,
    )
    value = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., 10 for 10%, or 10 for $10
    expiration_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # New Fields
    specific_customers = models.ManyToManyField(
        User,
        through='PromoCodeCustomer',
        related_name='promo_codes',
        blank=True,
        help_text="Specify users who are eligible for this promo code."
    )
    min_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum total purchase amount required to use the promo code."
    )
    min_purchase_period = models.DurationField(
        null=True,
        blank=True,
        help_text="Time period (e.g., 30 days) within which the minimum purchase amount should be met."
    )
    applicable_products = models.ManyToManyField(
        Product,
        through='PromoCodeProduct',
        related_name='promo_codes',
        blank=True,
        help_text="Specify products that must be purchased to use the promo code."
    )
    redemption_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of times this promo code can be redeemed."
    )
    new_customers_only = models.BooleanField(
        default=False,
        help_text="If set, only newly registered customers can use this promo code."
    )
    usage_limit_per_customer = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of times a single customer can redeem this promo code."
    )
    
    def save(self, *args, **kwargs):
        # Ensure the code is in uppercase
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    
    def is_valid(self, user=None, payload_products=None):
        return all([
            self.is_active,
            self.is_valid_customer(user),
            self.is_valid_product(payload_products),
            self.is_valid_min_purchase(user),
            self.is_valid_redemption_limit(user),
            self.is_valid_usage_limit_per_customer(user),
        ])
    

    def is_valid_customer(self, user=None):
        if not self.specific_customers.exists():
            return True
        if user is None:
            return False
        return self.specific_customers.filter(id=user).exists()

    def is_valid_new_customer(self, user=None):
        if self.new_customers_only:
            return self.is_new_customer(user)
        return True
    
    

    def is_valid_product(self, variants_aliases):
        if self.applicable_products.exists():
            for variants_alias in variants_aliases:
                if not self.applicable_products.filter(variants__alias=variants_alias).exists():
                    return False
        return True
    
    def is_valid_min_purchase(self, user=None):
        return self.has_min_purchase(user)
    
    def is_valid_redemption_limit(self, user=None):
        if self.redemption_limit is None:
            return True
        return self.get_total_redemptions() < self.redemption_limit
    
    def is_valid_usage_limit_per_customer(self, user=None):
        if self.usage_limit_per_customer is None:
            return True
        return self.get_user_redemptions(user) < self.usage_limit_per_customer

    
    def get_total_redemptions(self):
        return PromoCodeUsage.objects.filter(promo_code=self).count()
    
    def get_total_applicable_products(self):
        return self.applicable_products.count()
    
    def get_total_specific_customers(self):
        return self.specific_customers.count()
    
    def get_user_redemptions(self, user):
        return PromoCodeUsage.objects.filter(promo_code=self, user=user).count()
    
    def is_new_customer(self, user):
        # Define "new" as registered within the last 30 days
        return user.date_joined >= timezone.now() - timedelta(days=30)
    
    def has_min_purchase(self, user):
        from nxtbn.order.models import Order

        if not self.min_purchase_amount or not self.min_purchase_period:
            return True
        cutoff_date = timezone.now() - self.min_purchase_period
        result = Order.objects.filter(
            user=user,
            created_at__gte=cutoff_date,
            status__in=[OrderStatus.SHIPPED, OrderStatus.DELIVERED]
        ).aggregate(total=models.Sum('total_price'))
        total = result['total'] if result['total'] is not None else 0
        return total>=self.min_purchase_amount
    
    def has_applicable_products(self, user):
        from nxtbn.order.models import OrderLineItem

        # Check if the user has purchased at least one of the applicable products
        return OrderLineItem.objects.filter(
            order__user=user,
            order__status__in=[OrderStatus.PENDING, OrderStatus.SHIPPED, OrderStatus.DELIVERED],
            product__in=self.applicable_products.all()
        ).exists()
    
    def clean(self):
        if self.redemption_limit is not None and self.redemption_limit <= 0:
            raise ValidationError("Redemption limit must be a positive integer.")
        if self.min_purchase_amount is not None and self.min_purchase_amount < 0:
            raise ValidationError("Minimum purchase amount cannot be negative.")
        if self.specific_customers.exists() and self.new_customers_only:
            raise ValidationError("Cannot specify specific customers and new customers only.")
        if self.min_purchase_amount is not None and self.min_purchase_period is None:
            raise ValidationError("Must specify a time period for the minimum purchase amount.")
        
        super().clean()
    
    class Meta:
        verbose_name = "Promo Code"
        verbose_name_plural = "Promo Codes"



class PromoCodeUsage(AbstractBaseModel):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, help_text="Select the customer who redeemed this promo code.")
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, help_text="The promo code that was applied to the order.")
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, help_text="The order associated with the use of this promo code.")
    applied_at = models.DateTimeField(auto_now_add=True, help_text="The timestamp when the promo code was applied.")
    

class PromoCodeCustomer(models.Model):
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, help_text="The promo code that is restricted to specific customers.")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, help_text="The customer who is eligible to use this promo code.")
    
    class Meta:
        unique_together = ('promo_code', 'customer')
        verbose_name = "Promo Code Customer"
        verbose_name_plural = "Promo Code Customers"
    
    def __str__(self):
        return f"{self.promo_code.code} - {self.customer.username}"
    

class PromoCodeProduct(models.Model):
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, help_text="The promo code that applies to specific products.")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text="The product eligible for this promo code.")
    
    class Meta:
        unique_together = ('promo_code', 'product')
        verbose_name = "Promo Code Product"
        verbose_name_plural = "Promo Code Products"
    
    def __str__(self):
        return f"{self.promo_code.code} - {self.product.name}"


# ==================================================================
# Translation Models
# ==================================================================

class PromoCodeTranslation(AbstractTranslationModel):
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='translations')
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('language_code', 'promo_code')
        verbose_name = "Promo Code Translation"
        verbose_name_plural = "Promo Code Translations"
    
    def __str__(self):
        return f"{self.promo_code.code} ({self.language_code})"