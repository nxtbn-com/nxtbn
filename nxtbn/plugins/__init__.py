from django.db import models
from django.utils.translation import gettext_lazy as _

class PluginType(models.TextChoices):
    PAYMENT_PROCESSOR = 'PAYMENT_PROCESSOR', _('Payment Processor')
    CURRENCY_BACKEND = 'CURRENCY_BACKEND', _('Currency Backend')
    SMS_SERVICE = 'SMS_SERVICE', _('SMS Service')
    EMAIL_SERVICE = 'EMAIL_SERVICE', _('Email Service')
    INVOICE = 'INVOICE', _('Invoice')
    GENERAL = 'GENERAL', _('General')