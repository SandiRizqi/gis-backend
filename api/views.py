from django.shortcuts import render
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.gis.geos import GEOSGeometry
from rest_framework.parsers import JSONParser
from .models import FIRE_HOTSPOT
from .functions import *
import subprocess




@csrf_exempt
def ADD_HOTSPOT(request):
    if request.method == "POST":
        hotspot = JSONParser().parse(request)
        UID = int(hotspot['id'])
        CONF = int(hotspot['conf'])
        RADIUS = int(hotspot['radius'])
        DATE = str(hotspot['date'])
        TIME = str(hotspot['times'])
        SATELLITE = str(hotspot['sat']).upper()
        PROVINSI = str(hotspot['provinsi'])
        KEBUPATEN = str(hotspot['kabupaten'])
        KECAMATAN = str(hotspot['kecamatan'])
        geometry = hotspot['geometry']
        geom = GEOSGeometry(json.dumps(geometry))
        if not FIRE_HOTSPOT.objects.filter(UID=UID).exists():
            FIRE_HOTSPOT.objects.create(UID=UID, CONF=CONF, DATE=DATE, TIME=TIME, RADIUS=RADIUS, SATELLITE=SATELLITE, PROVINSI=PROVINSI, KEBUPATEN=KEBUPATEN, KECAMATAN=KECAMATAN, geom=geom)
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
