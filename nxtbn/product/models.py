from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError



from nxtbn.core import CurrencyTypes, MoneyFieldTypes
from nxtbn.core.mixin import MonetaryMixin
from nxtbn.core.models import AbstractMetadata, AbstractSEOModel, PublishableModel, AbstractBaseUUIDModel, AbstractBaseModel, NameDescriptionAbstract
from nxtbn.filemanager.models import Document, Image
from nxtbn.product import ProductType, StockStatus, WeightUnits
from nxtbn.users.admin import User

class Supplier(NameDescriptionAbstract, AbstractSEOModel):
    pass

class Category(NameDescriptionAbstract, AbstractSEOModel):
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategories'
    )

    def get_family_tree(self):
        family_tree = []
        current = self
        depth = 0
        while current is not None:
            family_tree.insert(0, {'depth': depth, 'name': current.name})
            current = current.parent
            depth += 1
        return family_tree

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
    
    def __str__(self):
        return self.name

    def clean(self):
        """Validate that category depth does not exceed 2 levels."""
        if self._get_depth() > 2:
            raise ValidationError("Category depth must not exceed 2 levels.")

    def _get_depth(self):
        """Recursively determine the depth of the category."""
        depth = 0
        current = self
        while current.parent:
            depth += 1
            current = current.parent
        return depth

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Collection(NameDescriptionAbstract, AbstractSEOModel):
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='collections_created'
    )
    last_modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='collections_modified'
    )
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='collection_images/', blank=True, null=True)

    class Meta:
        verbose_name = _("Collection")
        verbose_name_plural = _("Collections")

    def __str__(self):
        return self.name

class Product(PublishableModel, AbstractSEOModel):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='products_created')
    last_modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='products_modified', null=True, blank=True)
    name = models.CharField(max_length=255)
    summary = models.TextField(max_length=500)
    description = models.TextField(max_length=500)
    media = models.ManyToManyField(Document, blank=True)
    category = models.ForeignKey(
        'Category', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='products'
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='+', null=True, blank=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=25, default=ProductType.SIMPLE_PRODUCT, choices=ProductType.choices)
    related_to = models.ManyToManyField("self", blank=True)
    default_variant = models.OneToOneField(
        "ProductVariant",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    collections = models.ManyToManyField(Collection, blank=True, related_name='products_in_collection')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """
        Returns the absolute URL for this Product instance. 
        This URL is intended for use within the application, not for API endpoints.
        It is designed to be used in Jinja templates, and is automatically included in the sitemap.
        """
        return reverse("product_detail", args=[self.slug])


class ProductVariant(MonetaryMixin, AbstractMetadata, models.Model):
    money_validator_map = {
        "price": {
            "currency_field": "currency",
            "type": MoneyFieldTypes.UNIT,
            "require_base_currency": True,
        },
    }

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_image = models.ManyToManyField(Image, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    compare_at_price = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal('0.01'))])

    currency = models.CharField(
        max_length=3,
        default=CurrencyTypes.USD,
        choices=CurrencyTypes.choices,
    )
    price = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal('0.01'))])

    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal('0.01'))])

  
    track_inventory = models.BooleanField(default=True)

    # if track_inventory is enabled
    stock = models.IntegerField(default=0, verbose_name="Stock")
    low_stock_threshold = models.IntegerField(default=0, verbose_name="Stock")

    # if track_inventory is not enabled
    stock_status = models.CharField(default=StockStatus.IN_STOCK, choices=StockStatus.choices, max_length=15)

    color_code = models.CharField(max_length=7, null=True, blank=True)
    color_name = models.CharField(max_length=50, null=True, blank=True)

    sku = models.CharField(max_length=50, unique=True)
    weight_unit = models.CharField(
        max_length=5,
        choices=WeightUnits.choices,
        blank=True,
        null=True
    )
    weight_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('price',)  # Order by price ascending
    
    def save(self, *args, **kwargs):
        self.validate_amount()
        super(ProductVariant, self).save(*args, **kwargs)

    def __str__(self):
        variant_name = self.name if self.name else 'Default'
        return f"{self.product.name} - {variant_name} (SKU: {self.sku})"
