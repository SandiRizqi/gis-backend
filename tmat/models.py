from django.contrib.gis.db import models
import json
from django.contrib.gis.geos import GEOSGeometry

# Create your models here.
class TMAT_LOCATIONS(models.Model):
    code = models.CharField(max_length=100)
    werks = models.IntegerField()
    afd_name = models.CharField(max_length=100)
    block_name = models.CharField(max_length=100)
    no = models.CharField(max_length=100)
    soil = models.CharField(max_length=100)
    longitude = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    latitude = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    geojson = models.FileField(upload_to='geojson', blank=True, null=True, verbose_name='TMAT_geojson_file')
    geom = models.PointField(srid=4326, geography=True, null=True, blank=True, editable=True)

    def __str__(self):
        return f"{self.code} - {self.afd_name} - {self.block_name}"
    
    def save(self, *args, **kwargs):
        if self.geojson:
            # Load the geojson object
            objects = json.load(self.geojson)
            coordinates = objects['features'][0]['geometry']['coordinates']

            point = {
                "type": "Point",
                "coordinates": coordinates  # Coordinates should be a pair [lon, lat]
            }

            # Convert the point to a GEOSGeometry object and assign it to self.geom
            self.geom = GEOSGeometry(json.dumps(point))

        # Call the parent save method
        super().save(*args, **kwargs)
