from django.contrib import admin
from .models import PALMS_COMPANY_LIST, FIRE_EVENTS_ALERT_LIST, FIRE_HOTSPOT, DEFORESTATIONS_EVENTS_ALERT_LIST
from leaflet.admin import LeafletGeoAdmin



class COMPAdmin(LeafletGeoAdmin):
    list_display = ('COMP_NAME', 'COMP_GROUP')
    search_fields = ('COMP_NAME', 'COMP_GROUP')
    list_filter = ['COMP_NAME']

class FireEventsAdmin(admin.ModelAdmin):
    model = FIRE_EVENTS_ALERT_LIST
    ordering = ('-EVENT_DATE',)
    list_display = ["COMP_NAME", "COMP_GROUP", "EVENT_DATE", "UPDATE_TIME", "distance", "STATUS", "CATEGORY"]
    list_filter = ["COMP_NAME", "COMP_GROUP"]
    search_fields = ("COMP_NAME", "COMP_GROUP", "STATUS", "CATEGORY")

class FireHotspotAdmin(admin.ModelAdmin):
    model = FIRE_HOTSPOT
    ordering = ('-DATE',)
    list_display = ["UPDATE_TIME","DATE", "TIME", "CONF", "SATELLITE", "SOURCE"]
    list_filter = ["SOURCE", "DATE"]

class DFEventsAdmin(admin.ModelAdmin):
    model = DEFORESTATIONS_EVENTS_ALERT_LIST
    ordering = ('-ALERT_DATE',)
    list_display = ["COMP", "EVENT_ID", "ALERT_DATE", "CREATED", "UPDATED", "AREA"]
    list_filter = ["COMP"]
    search_fields = ("COMP", "EVENT_ID")
    


admin.site.register(PALMS_COMPANY_LIST, COMPAdmin)
admin.site.register(FIRE_EVENTS_ALERT_LIST, FireEventsAdmin)
admin.site.register(FIRE_HOTSPOT, FireHotspotAdmin)
admin.site.register(DEFORESTATIONS_EVENTS_ALERT_LIST, DFEventsAdmin)





