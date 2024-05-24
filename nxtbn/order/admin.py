from django.contrib import admin
from nxtbn.order.models import Address,Order,OrderLineItem

# Register your models here.


class AddressAdmin(admin.ModelAdmin):
    list_display = ('id','first_name', 'last_name', 'street_address', 'city', 'country')
    list_filter = ('is_default_delivery_address',)
    search_fields = ('first_name', 'last_name', 'street_address', 'city', 'country')

admin.site.register(Address, AddressAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'humanize_total_price', 'payment_method', 'shipping_address', 'billing_address', 'total_price', 'status')
    list_filter = ('status', 'payment_method', 'vendor')
    search_fields = ('user', 'vendor', 'payment_method', 'shipping_address', 'billing_address', 'total_price')

admin.site.register(Order, OrderAdmin)


class OrderLineItemAdmin(admin.ModelAdmin):
    list_display = ('id','variant', 'quantity', 'price_per_unit', 'total_price')
    list_filter = ('variant', 'order')
    search_fields = ('variant', 'order')


admin.site.register(OrderLineItem, OrderLineItemAdmin)