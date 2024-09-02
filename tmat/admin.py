from django.contrib import admin
from .models import TMAT_LOCATIONS

class TMAT_LOCATIONSAdmin(admin.ModelAdmin):
    list_display = ('code', 'werks', 'afd_name', 'block_name', 'no', 'soil', 'longitude', 'latitude')
    search_fields = ('code', 'afd_name', 'block_name', 'no')
    list_filter = ('werks', 'afd_name', 'block_name', 'soil')
    readonly_fields = ('geom',)
    
    def save_model(self, request, obj, form, change):
        # Automatically set geom when saving through admin
        obj.save()

admin.site.register(TMAT_LOCATIONS, TMAT_LOCATIONSAdmin)
