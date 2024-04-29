from rest_framework import serializers
from .models import FIRE_EVENTS_ALERT_LIST, DEFORESTATIONS_EVENTS_ALERT_LIST



class FireEventSerilizer(serializers.ModelSerializer):

    class Meta:
        model = FIRE_EVENTS_ALERT_LIST
        fields = '__all__'


class DeforestationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DEFORESTATIONS_EVENTS_ALERT_LIST
        fields = ['id','ALERT_DATE', 'CONF', 'AREA', 'COMP']