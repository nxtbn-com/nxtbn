from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.contrib import messages

from nxtbn.core.models import CurrencyExchange, SiteSettings
from nxtbn.core.currency.utils import currency_Backend

admin.site.register(SiteSettings)


def refresh_currency_rates(modeladmin, request, queryset):
    backend = currency_Backend()
    backend.refresh_rate()
    messages.success(request, "Currency rates refreshed successfully.")
@admin.register(CurrencyExchange)
class CurrencyExchangeAdmin(admin.ModelAdmin): # TODO: Distable refresh buttion when user not in DEBUG mode
    list_display = ('base_currency', 'target_currency', 'humanize_rate', 'created_at', 'last_modified')
    actions = [refresh_currency_rates]