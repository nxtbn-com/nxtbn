
from django.contrib import admin
from nxtbn.vendor.models import Vendor

# Register your models here.

class VendorAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'contact_info')
    list_filter = ('name',)
    search_fields = ('name', 'contact_info')

admin.site.register(Vendor, VendorAdmin)