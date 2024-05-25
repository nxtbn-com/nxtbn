from django.contrib import admin

from nxtbn.core.models import CurrencyExchange, SiteSettings

admin.site.register(SiteSettings)
admin.site.register(CurrencyExchange)
