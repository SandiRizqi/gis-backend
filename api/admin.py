from django.contrib import admin
from .models import PALMS_COMPANY_LIST, FIRE_EVENTS_ALERT_LIST, FIRE_HOTSPOT, DEFORESTATIONS_EVENTS_ALERT_LIST
from leaflet.admin import LeafletGeoAdmin


class COMPAdmin(LeafletGeoAdmin):
    list_display = ('COMP_NAME', 'COMP_GROUP')
    search_fields = ('COMP_NAME', 'COMP_GROUP')
    list_filter = ['COMP_NAME']

class FireEventsAdmin(admin.ModelAdmin):
    model = FIRE_EVENTS_ALERT_LIST
    ordering = ('-EVENT_ID',)
    list_display = ["EVENT_ID", "COMP_NAME", "EVENT_DATE", "distance"]


admin.site.register(PALMS_COMPANY_LIST, COMPAdmin)
admin.site.register(FIRE_EVENTS_ALERT_LIST, FireEventsAdmin)
admin.site.register(FIRE_HOTSPOT)
admin.site.register(DEFORESTATIONS_EVENTS_ALERT_LIST)