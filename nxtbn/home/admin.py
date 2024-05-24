from django.contrib import admin
from nxtbn.home.models import MetaGlobal

# Register your models here.


class MetaGlobalAdmin(admin.ModelAdmin):
    list_display = ('id','logo',)


admin.site.register(MetaGlobal,MetaGlobalAdmin)