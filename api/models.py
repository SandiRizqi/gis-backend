from django.contrib.gis.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
import json
from django.contrib.gis.geos import GEOSGeometry

event_status = (
    ("ACTIVE", "ACTIVE"),
    ("INACTIVE", "INACTIVE")
)
fire_cat = (
    ("AMAN", "AMAN"),
    ("PERHATIAN", "PERHATIAN"),
    ("WASPADA", "WASPADA"),
    ("BAHAYA", "BAHAYA")
)

sources = (("LAPAN", "LAPAN"),
           ("SIPONGI", "SIPONGI"))

class PALMS_COMPANY_LIST(models.Model):
    COMP_NAME = models.CharField(max_length=250)
    COMP_GROUP = models.CharField(max_length=250, null=True, blank=True)
    CREATED = models.DateTimeField(default=timezone.now)
    UPDATED = models.DateTimeField(auto_now=True)
    geom = models.MultiPolygonField(srid=4326, geography=True, null=True, blank=True, editable=True)
    geojson = models.FileField(upload_to='geojson', blank=True, null=True, verbose_name='HGU_geojson_file')

    def __str__(self):
        return '{}'.format(str(self.COMP_NAME))
    
    def save(self, *args, **kwargs):

        if self.geojson:
            objects = json.load(self.geojson)
            coordinates = list()
            for ft in objects['features']:
                geom_str = ft['geometry']['coordinates']
                coordinates.append(geom_str)
            print(coordinates)
            multipolygon = {
                "type": "MultiPolygon",
                "coordinates": coordinates
            }
            self.geom = GEOSGeometry(json.dumps(multipolygon))
        super().save(*args, **kwargs)

    
    

    
class FIRE_HOTSPOT(models.Model):
    UID = models.CharField(max_length=250)
    DATE = models.DateField(default=timezone.now)
    TIME = models.TimeField()
    CONF = models.IntegerField()
    SATELLITE = models.CharField(max_length=20)
    RADIUS = models.IntegerField()
    KECAMATAN = models.CharField(max_length=100)
    KEBUPATEN = models.CharField(max_length=100)
    PROVINSI = models.CharField(max_length=100)
    SOURCE = models.CharField(max_length=50, choices=sources, blank=True, null=True)
    LONG = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    LAT = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    geom = models.PointField(srid=4326, geography=True, null=True, blank=True, editable=True)

    class Meta:
        ordering = ['-UID']




class FIRE_EVENTS_ALERT_LIST(models.Model):
    COMP = models.ForeignKey(PALMS_COMPANY_LIST, on_delete=models.CASCADE, related_name='comp_fire', default="")
    COMP_NAME = models.CharField(max_length=250)
    COMP_GROUP = models.CharField(max_length=250, null=True, blank=True)
    EVENT_ID = models.BigIntegerField()
    EVENT_DATE = models.DateField(default=timezone.now)
    EVENT_TIME = models.TimeField()
    CONF = models.IntegerField()
    SATELLITE = models.CharField(max_length=20)
    RADIUS = models.IntegerField()
    KECAMATAN = models.CharField(max_length=100)
    KEBUPATEN = models.CharField(max_length=100)
    PROVINSI = models.CharField(max_length=100)
    distance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    STATUS = models.CharField(max_length=50, choices=event_status, blank=True, null=True, default="ACTIVE")
    CATEGORY = models.CharField(max_length=50, choices=fire_cat, blank=True, null=True, default="AMAN")
    geom = models.PointField(srid=4326, geography=True, null=True, blank=True, editable=True)

    class Meta:
        ordering = ['-EVENT_ID']

    def __str__(self):
        return '{}-{}'.format(str(self.EVENT_ID), self.COMP_NAME)

# Create your models here.
class DEFORESTATIONS_EVENTS_ALERT_LIST(models.Model):
    COMP = models.ForeignKey(PALMS_COMPANY_LIST, on_delete=models.CASCADE, related_name='comp_list', default="")
    EVENT_ID = models.CharField(max_length=250)
    ALERT_DATE = models.DateTimeField(default=timezone.now)
    CREATED = models.DateTimeField(default=timezone.now)
    UPDATED = models.DateTimeField(auto_now=True)
    AREA = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    READ_BY = ArrayField(models.CharField(max_length=250, null=True, blank=True), default=list, blank=True, null=True)
    geom = models.MultiPolygonField(srid=4326, geography=True, null=True, blank=True, editable=True)

    class Meta:
        ordering = ['-ALERT_DATE']
 
    def __str__(self):
        return '{}-{}'.format(str(self.COMP), self.ALERT_DATE)