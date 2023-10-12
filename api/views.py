from django.shortcuts import render
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.gis.geos import GEOSGeometry
from django.core.serializers import serialize
from .models import FIRE_HOTSPOT, FIRE_EVENTS_ALERT_LIST, PALMS_COMPANY_LIST, DEFORESTATIONS_EVENTS_ALERT_LIST
from .serializers import *
import subprocess
from turfpy.measurement import area
import json
from gisbackend.settings import ENV_URL


from rest_framework.parsers import JSONParser
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def LIST_COMPANY(request):
    id = int(request.GET['comp'])
    if not id :
        COMP = PALMS_COMPANY_LIST.objects.all()
    else:
        COMP = PALMS_COMPANY_LIST.objects.filter(pk=int(id))
    data = serialize('geojson', COMP, fields=('pk', 'COMP_NAME', 'COMP_GROUP'), geometry_field='geom')
    return HttpResponse(data, content_type='application/json')

@csrf_exempt
def ADD_HOTSPOT(request):
    if request.method == "POST":
        hotspot = JSONParser().parse(request)
        UID = hotspot['id']
        CONF = int(hotspot['conf'])
        RADIUS = int(hotspot['radius'])
        SOURCE = str(hotspot['source'])
        LONG = round(float(hotspot['long']), 3)
        LAT = round(float(hotspot['lat']), 3)
        DATE = str(hotspot['date'])
        TIME = str(hotspot['times'])
        SATELLITE = str(hotspot['sat']).upper()
        PROVINSI = str(hotspot['provinsi'])
        KEBUPATEN = str(hotspot['kabupaten'])
        KECAMATAN = str(hotspot['kecamatan'])
        geometry = hotspot['geometry']
        geom = GEOSGeometry(json.dumps(geometry))
        if not FIRE_HOTSPOT.objects.filter(DATE=DATE, LONG=LONG, LAT=LAT).exists():
            FIRE_HOTSPOT.objects.create(UID=UID, CONF=CONF, DATE=DATE, TIME=TIME, RADIUS=RADIUS, SATELLITE=SATELLITE, PROVINSI=PROVINSI, KEBUPATEN=KEBUPATEN, KECAMATAN=KECAMATAN, SOURCE=SOURCE, LONG=LONG, LAT=LAT, geom=geom)
            return JsonResponse({"message": "Added Successfully" })
        else:
            return JsonResponse({"message": "Data Already Exist" })

@csrf_exempt
def GET_HOTSPOT(request):
    if request.method == "GET":
        subprocess.Popen(['python', './function/getHotspot.py'])
        return JsonResponse({
            "message": "Function is running in the background"
        })
    
@csrf_exempt
def GET_HOTSPOT_ALERT(request):
    if request.method == "GET":
        subprocess.Popen(['python', './function/getHotspotAlert.py'])
        return JsonResponse({
            "message": "Function is running in the background"
        })
    

@csrf_exempt
def LIST_HOTSPOT(request):
    conf = int(request.GET['conf'])
    startdate = str(request.GET['startdate'])
    enddate = str(request.GET['enddate'])
    if conf:
        HOTSPOTS = FIRE_HOTSPOT.objects.filter(DATE__range=[startdate, enddate], CONF=conf)
    else:
        HOTSPOTS = FIRE_HOTSPOT.objects.filter(DATE__range=[startdate, enddate])
    data = serialize('geojson', HOTSPOTS, fields=('UID', 'DATE', 'TIME', 'CONF', 'RADIUS', 'KECAMATAN', 'KEBUPATEN', 'PROVINSI', 'SATELLITE'), geometry_field='geom')
    return HttpResponse(data, content_type='application/json')

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def LIST_FIRE_EVENTS(request):
    if request.method == "GET":
        COMP = int(request.GET['comp'])
        status = request.GET['status']
        if COMP:
            events = FIRE_EVENTS_ALERT_LIST.objects.filter(COMP=COMP, STATUS=status)
        else:
            events = FIRE_EVENTS_ALERT_LIST.objects.filter(STATUS=status)
        
        data = serialize('geojson', events, fields=('COMP', 'COMP_GROUP','COMP_NAME', 'EVENT_DATE', 'EVENT_TIME','EVENT_CAT', 'CONF', 'SATELLITE', 'RADIUS', "STATUS","CATEGORY", "distance"), geometry_field='geom')
        return HttpResponse(data, content_type='application/json')
    
    if request.method == "POST":
        data = JSONParser().parse(request)
        if not FIRE_EVENTS_ALERT_LIST.objects.filter(EVENT_DATE=data['EVENT_DATE'], LONG=data['LONG'], LAT=data['LAT']).exists():
            PT = PALMS_COMPANY_LIST.objects.get(pk=data['COMP'])
            COMP = PT
            COMP_NAME = data['COMP_NAME']
            COMP_GROUP = data['COMP_GROUP']
            #EVENT_ID = data['EVENT_ID']
            EVENT_DATE = data['EVENT_DATE']
            EVENT_TIME = data['EVENT_TIME']
            CONF = data['CONF']
            SATELLITE = data['SATELLITE']
            RADIUS = data['RADIUS']
            KECAMATAN = data['KECAMATAN']
            KEBUPATEN = data['KEBUPATEN']
            PROVINSI = data['PROVINSI']
            distance = data['distance']
            CATEGORY = data['CATEGORY']
            LONG = data['LONG']
            LAT= data['LAT']
            geom = {
                "type": "Point",
                "coordinates": data['coordinates']}
            geom = GEOSGeometry(json.dumps(geom))
            FIRE_EVENTS_ALERT_LIST.objects.create(COMP=COMP, COMP_NAME=COMP_NAME, COMP_GROUP=COMP_GROUP, EVENT_DATE=EVENT_DATE, EVENT_TIME=EVENT_TIME, SATELLITE=SATELLITE, RADIUS=RADIUS, CONF=CONF, KECAMATAN=KECAMATAN, KEBUPATEN=KEBUPATEN, PROVINSI=PROVINSI, distance=distance, geom=geom, CATEGORY=CATEGORY, LONG=LONG, LAT=LAT)
            return JsonResponse({"message": "Added Successfully" })
        else:
            return JsonResponse({"message": "Data Already Exist" })



class FireAlertAPIViewset(viewsets.ModelViewSet):
    queryset = FIRE_EVENTS_ALERT_LIST.objects.all()
    serializer_class = FireEventSerilizer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
@csrf_exempt   
def GET_DEFORESTATIONS(request):
    #print(ENV_URL)
    subprocess.Popen(['python', './function/getDF.py', ' -env ' + '{}'.format(ENV_URL)])
    return JsonResponse({
        "message": "POST Successfully"
    })


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def ADD_DEFORESTATION_ALERT(request):
    if request.method == "POST":
        df = JSONParser().parse(request)
        comp_id = df['id']
        COMP = PALMS_COMPANY_LIST.objects.get(id=int(comp_id))
        EVENT_ID=df['event_id']
        AREA=df['area']
        ALERT_DATE=df['alert_date']
        geometry = df['geometry']
        geom = GEOSGeometry(json.dumps(geometry))
        if not DEFORESTATIONS_EVENTS_ALERT_LIST.objects.filter(EVENT_ID=EVENT_ID).exists():
            DEFORESTATIONS_EVENTS_ALERT_LIST.objects.create(COMP=COMP, EVENT_ID=EVENT_ID, AREA=AREA, ALERT_DATE=ALERT_DATE, geom=geom)
            return JsonResponse({"message": "Added Successfully" })
        else:
            Event = DEFORESTATIONS_EVENTS_ALERT_LIST.objects.get(COMP=COMP, EVENT_ID=EVENT_ID)
            Event.AREA = AREA
            Event.geom = geom
            Event.save()
            return JsonResponse({"message": "Data already Exist Updated" })