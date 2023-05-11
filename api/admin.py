from django.contrib import admin
from .models import PALMS_COMPANY_LIST
from leaflet.admin import LeafletGeoAdmin


class COMPAdmin(LeafletGeoAdmin):
    list_display = ('COMP_NAME', 'COMP_GROUP')
    search_fields = ('COMP_NAME', 'COMP_GROUP')
    list_filter = ['COMP_NAME']


admin.site.register(PALMS_COMPANY_LIST, COMPAdmin)