from django.db import models

class WeightUnits(models.TextChoices):
    """Defines standard units of weight for product measurement.

    - 'GRAM': Weight in grams.
    - 'KILOGRAM': Weight in kilograms.
    - 'POUND': Weight in pounds.
    - 'OUNCE': Weight in ounces.
    - 'TON': Weight in tons.
    """

    GRAM = 'GRAM', 'Gram'
    KILOGRAM = 'KG', 'Kilogram'
    POUND = 'LB', 'Pound'
    OUNCE = 'OZ', 'Ounce'
    TON = 'TON', 'Ton'


class ProductType(models.TextChoices):
    """Defines different types of products in a catalog.

    - 'SIMPLE_PRODUCT': A single, standalone product.
    - 'GROUPED_PRODUCT': A collection of related products or services.
    - 'EXTERNAL_PRODUCT': A product sold through an affiliate or external source.
    - 'VARIABLE_PRODUCT': A product with different variations (e.g., size, color).
    - 'SIMPLE_SUBSCRIPTION': A single subscription-based product.
    - 'VARIABLE_SUBSCRIPTION': A subscription-based product with multiple variations.
    - 'PRODUCT_BUNDLE': A bundle of multiple products sold together.
    """

    SIMPLE_PRODUCT = 'SIMPLE_PRODUCT', 'Simple Product'
    GROUPED_PRODUCT = 'GROUPED_PRODUCT', 'Grouped Product'
    EXTERNAL_PRODUCT = 'EXTERNAL_PRODUCT', 'External/Affiliate Product'
    VARIABLE_PRODUCT = 'VARIABLE_PRODUCT', 'Variable Product'
    SIMPLE_SUBSCRIPTION = 'SIMPLE_SUBSCRIPTION', 'Simple Subscription'
    VARIABLE_SUBSCRIPTION = 'VARIABLE_SUBSCRIPTION', 'Variable Subscription'
    PRODUCT_BUNDLE = 'PRODUCT_BUNDLE', 'Product Bundle'


class StockStatus(models.TextChoices):
    """Defines the stock availability status for products.

    - 'IN_STOCK': The product is available and in stock.
    - 'OUT_OF_STOCK': The product is currently out of stock.
    """

    IN_STOCK = 'IN_STOCK', 'In Stock'
    OUT_OF_STOCK = 'OUT_OF_STOCK', 'Out of Stock'
