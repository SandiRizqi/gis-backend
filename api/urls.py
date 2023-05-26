from django.urls import path, include
from . import views
from .router import router


urlpatterns = [
    path('addhotspot/', views.ADD_HOTSPOT),
    path('gethotspot/', views.GET_HOTSPOT),
    path('gethotspotalert/', views.GET_HOTSPOT_ALERT),
    path('hotspot/', views.LIST_HOTSPOT),
    path('hotspotevents/', views.LIST_FIRE_EVENTS),
    path('endpoints/', include(router.urls), name="endpoints" ),
    path('getdeforestations/', views.GET_DEFORESTATIONS),
]