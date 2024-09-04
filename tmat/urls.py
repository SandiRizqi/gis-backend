from django.urls import path
from .views import tmat_location_data_chart, tmat_location_percentage_data_chart

urlpatterns = [
    path('tmat-location-data/', tmat_location_data_chart, name='tmat_location_data_chart'),
    path('tmat-location-data-percentage/', tmat_location_percentage_data_chart, name='tmat_location_data__percentage_chart'),
]
