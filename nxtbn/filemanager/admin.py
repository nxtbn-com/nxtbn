from django.contrib import admin
from nxtbn.filemanager.models import Image,Document

# Register your models here.


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'created_by', 'last_modified_by')
    list_filter = ('created_by', 'last_modified_by')
    search_fields = ('name', 'image_alt_text')
    readonly_fields = ('last_modified_by',) 

admin.site.register(Image,ImageAdmin)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'created_by', 'last_modified_by')
    list_filter = ('created_by', 'last_modified_by')
    search_fields = ('name', 'image_alt_text')
    readonly_fields = ('last_modified_by',) 

admin.site.register(Document, DocumentAdmin)
