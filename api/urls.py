from django.urls import path
from . import views


urlpatterns = [
    path('addhotspot/', views.ADD_HOTSPOT),
    path('gethotspot/', views.GET_HOTSPOT)
]