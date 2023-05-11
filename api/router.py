from rest_framework import routers
from .views import FireAlertAPIViewset


router = routers.DefaultRouter()
router.register('fireevents', FireAlertAPIViewset)