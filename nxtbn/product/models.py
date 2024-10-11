from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError



from nxtbn.core import CurrencyTypes, MoneyFieldTypes
from nxtbn.core.mixin import MonetaryMixin
from nxtbn.core.models import AbstractMetadata, AbstractSEOModel, AbstractUUIDModel, PublishableModel, AbstractBaseUUIDModel, AbstractBaseModel, NameDescriptionAbstract, no_nested_values
from nxtbn.filemanager.models import Document, Image
from nxtbn.product import DimensionUnits, StockStatus, WeightUnits
from nxtbn.tax.models import TaxClass
from nxtbn.users.admin import User
from django.db.models import Q

class Supplier(NameDescriptionAbstract, AbstractSEOModel):
    pass

class Color(AbstractBaseModel):
    code = models.CharField(max_length=7, unique=True)
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")

class Category(NameDescriptionAbstract, AbstractSEOModel):
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategories'
    )

    def has_sub(self):
        return self.subcategories.exists()

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
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _("Collection")
        verbose_name_plural = _("Collections")

    def __str__(self):
        return self.name

class ProductTag(models.Model):
    name = models.CharField(unique=True, max_length=50)

class ProductType(models.Model):
    name = models.CharField(unique=True, max_length=50)
    taxable = models.BooleanField(default=False)
    physical_product = models.BooleanField(default=False)
    track_stock = models.BooleanField(default=False)
    has_variant = models.BooleanField(default=False)
    weight_unit = models.CharField(
        max_length=5,
        choices=WeightUnits.choices,
        blank=True,
        null=True
    )
    # TO DO: class Meta: # Handle unique together with each field except name

class Product(PublishableModel, AbstractMetadata, AbstractSEOModel):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='products_created')
    last_modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='products_modified', null=True, blank=True)
    name = models.CharField(max_length=255, help_text="The name of the product.")
    summary = models.TextField(max_length=500, help_text="A brief summary of the product.")
    description = models.TextField(max_length=5000)
    images = models.ManyToManyField(Image, blank=True)
    category = models.ForeignKey(
        'Category',
        on_delete=models.PROTECT, 
        related_name='products'
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='+', null=True, blank=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    product_type = models.ForeignKey(ProductType, related_name='product', on_delete=models.PROTECT, help_text="The type of product.")
    related_to = models.ManyToManyField("self", blank=True)
    default_variant = models.OneToOneField(
        "ProductVariant",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    collections = models.ManyToManyField(Collection, blank=True, related_name='products_in_collection')
    tags = models.ManyToManyField(ProductTag, blank=True)
    tax_class = models.ForeignKey(TaxClass, on_delete=models.PROTECT, related_name='products', null=True, blank=True) # null for tax exempt products

    class Meta:
        ordering = ('name',)

    def product_thumbnail(self, request):
        """
        Returns the URL of the first image associated with the product. 
        If no image is available, returns None.
        """
        first_image = self.images.first()  # Get the first image if it exists
        if first_image and hasattr(first_image, 'image') and first_image.image:
            image_url = first_image.image.url
            full_url = request.build_absolute_uri(image_url)
            return full_url
        return None

    
    def colors(self):
        return self.variants.values_list('color_code', flat=True).distinct()
    
    def get_stock(self):
        return self.variants.aggregate(stock=models.Sum('stock'))['stock']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """
        Returns the absolute URL for this Product instance. 
        This URL is intended for use within the application, not for API endpoints.
        It is designed to be used in Jinja templates, and is automatically included in the sitemap.
        """
        return reverse("product_detail", args=[self.slug])


class ProductVariant(MonetaryMixin, AbstractUUIDModel, models.Model):
    money_validator_map = {
        "price": {
            "currency_field": "currency",
            "type": MoneyFieldTypes.UNIT,
            "require_base_currency": True,
        },
    }

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_image = models.ForeignKey(Image, blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, blank=True, null=True)

    compare_at_price = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal('0.01'))], null=True, blank=True)

    currency = models.CharField(
        max_length=3,
        default=CurrencyTypes.USD,
        choices=CurrencyTypes.choices,
    )
    price = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal('0.01'))])

    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal('0.01'))])

  
    track_inventory = models.BooleanField(default=False)
    allow_backorder = models.BooleanField(default=False, help_text="Allow orders even if out of stock.")

    # if track_inventory is enabled
    stock = models.IntegerField(default=0, verbose_name="Stock")
    low_stock_threshold = models.IntegerField(default=0, verbose_name="Stock", help_text="Threshold to trigger low stock alert.")

    # if track_inventory is not enabled
    stock_status = models.CharField(default=StockStatus.IN_STOCK, choices=StockStatus.choices, max_length=15)

    sku = models.CharField(max_length=50, unique=True)


    color_code = models.CharField(max_length=7, null=True, blank=True)
    # Weight and dimensions are also types of attributes, but we created these fields separately for shipping rate calculation purposes.
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
    dimensions = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=DimensionUnits.choices,
        help_text="Format: Height x Width x Depth"
    )
    dimensions_value = models.CharField(max_length=50, blank=True, null=True)


    attributes = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        validators=[no_nested_values],
        help_text="A JSON field to store custom attributes for the variant. Primary attributes include color code, dimension, and weight value. Weight value and dimension are used for shipping calculations. This field allows adding as many custom attributes as needed."
    )



    class Meta:
        ordering = ('price',)  # Order by price ascending

    def clean(self):
        """
        Custom validation to ensure unique attribute's value combinations for variants under the same product.
        """
        super().clean()  # Call the base class clean method
        
        # Check if the attributes are provided
        if not self.attributes:
            return
        
        # Create a dynamic query based on the attributes provided for the variant
        query = Q(product=self.product)
        
        for key, value in self.attributes.items():
            if value:
                # Construct a dynamic query to match the key-value pairs in the attributes field
                query &= Q(**{f'{key}': value})
        
        # Exclude the current instance from the check if it's an update
        if self.pk:
            query &= ~Q(pk=self.pk)
        
        # Check if any variant with the same attribute combination already exists for the same product
        if ProductVariant.objects.filter(query).exists():
            raise ValidationError(
                f"A variant with the same attribute's key, value combination already exists for this product: {self.attributes}"
            )

    
    def save(self, *args, **kwargs):
        self.validate_amount()
        super(ProductVariant, self).save(*args, **kwargs)

    def __str__(self):
        variant_name = self.name if self.name else 'Default'
        return f"{self.product.name} - {variant_name} (SKU: {self.sku})"
