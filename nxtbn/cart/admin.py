from django.contrib import admin
from nxtbn.cart.models import  CartItem

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    list_filter = ('user',)
    search_fields = ('id', 'user')

admin.site.register(CartItem, CartItemAdmin)