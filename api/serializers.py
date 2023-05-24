from rest_framework import serializers
from .models import FIRE_EVENTS_ALERT_LIST



class FireEventSerilizer(serializers.ModelSerializer):

    class Meta:
        model = FIRE_EVENTS_ALERT_LIST
        fields = '__all__'