from django.db import models
from django_countries.fields import CountryField
from core.models import AbstractBaseModel

class TaxClass(models.Model):
    """
    TaxClass model represents a category of tax that can be applied to products.
    This model allows for the grouping of various tax rates under a common tax class.
    
    Attributes:
        name (str): The name of the tax class (e.g., VAT, GST, Sales Tax).
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Tax Class"
        verbose_name_plural = "Tax Classes"


class TaxRate(AbstractBaseModel):
    """
    TaxRate model represents a specific tax rate applied to a product within a certain jurisdiction.
    This model links tax rates to tax classes and allows for exemptions and activation status.
    
    Attributes:
        country (CountryField): The country where the tax rate is applicable.
        state (str): The state or province where the tax rate is applicable (optional).
        rate (Decimal): The tax rate as a percentage.
        tax_class (ForeignKey): The tax class to which this rate belongs.
        is_active (bool): Indicates if the tax rate is currently active.
        exempt_products (ManyToManyField): Products that are exempt from this tax rate.
    """
    country = CountryField()
    state = models.CharField(max_length=2, blank=True, null=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_class = models.ForeignKey(TaxClass, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    exempt_products = models.ManyToManyField('Product', blank=True)

    def is_applicable(self, product=None):
        """
        Determines if the tax rate is applicable based on product exemptions and activation status.
        
        Args:
            product (Product): The product to check for exemptions (optional).
        
        Returns:
            bool: True if the tax rate is applicable, False otherwise.
        """
        if product and product in self.exempt_products.all():
            return False
        return self.is_active

    def __str__(self):
        return f"{self.country} - {self.state if self.state else 'N/A'}: {self.tax_class.name} {self.rate}%"

    class Meta:
        unique_together = ('country', 'state', 'tax_class')
        ordering = ['country', 'state', 'tax_class']
        verbose_name = "Tax Rate"
        verbose_name_plural = "Tax Rates"
