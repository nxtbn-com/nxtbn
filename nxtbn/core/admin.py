from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.contrib import messages

from nxtbn.core.models import CurrencyExchange, SiteSettings
from nxtbn.core.currency.backend import currency_Backend

admin.site.register(SiteSettings)




@admin.register(CurrencyExchange)
class CurrencyExchangeAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'humanize_rate', 'created_at', 'last_modified')
    change_list_template = "admin/currency_exchange_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('refresh-rates/', self.admin_site.admin_view(self.refresh_rates), name='refresh-rates'),
        ]
        return custom_urls + urls

    def refresh_rates(self, request):
        if settings.DEBUG:  # Only allow refresh in DEBUG mode
            backend = currency_Backend()
            backend.refresh_rate()
            messages.success(request, "Currency rates refreshed successfully.")
        else:
            messages.error(request, "Currency rates refresh is disabled in production.")
        return HttpResponseRedirect("../")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['debug'] = settings.DEBUG
        return super(CurrencyExchangeAdmin, self).changelist_view(request, extra_context=extra_context)