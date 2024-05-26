from django.contrib import admin

from nxtbn.core.models import CurrencyExchange, SiteSettings

admin.site.register(SiteSettings)


@admin.register(CurrencyExchange)
class CurrencyExchangeAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'humanize_rate', 'created_at', 'last_modified')
    