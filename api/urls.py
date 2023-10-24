from django.urls import path, include
from . import views
from .router import router


urlpatterns = [
    path('addhotspot/', views.ADD_HOTSPOT),
    path('hotspot/', views.LIST_HOTSPOT),
    path('events/fires/company/', views.LIST_FIRE_EVENTS),
    path('listcompany/', views.LIST_COMPANY),
    path('endpoints/', include(router.urls), name="endpoints" ),
    path('getdeforestations/', views.GET_DEFORESTATIONS),
    path('updatedeforestations/', views.updatedeforestation),
    path('updatehotspots/', views.updatehotspot),
    path('adddeforestations/', views.ADD_DEFORESTATION_ALERT),
]