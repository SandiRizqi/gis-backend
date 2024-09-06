from django.contrib.gis.db import models
import json
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError

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
    keterangan = models.CharField(max_length=100, blank=True, null=True)
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




class TMAT_LOCATION_DATA(models.Model):
    tmat_location = models.ForeignKey(TMAT_LOCATIONS, on_delete=models.CASCADE)  # Reference to TMAT_LOCATIONS
    tahun = models.PositiveIntegerField()  # Year
    bulan = models.PositiveSmallIntegerField()  # Month, 1-12
    hari = models.PositiveSmallIntegerField()  # Day, 1-31
    periode = models.PositiveIntegerField()  # Period
    nilai = models.IntegerField(null=True, blank=True)  # Allow null and blank values
    input_date = models.CharField(max_length=11, blank=True, null=True)  # Date string in 'YYYYMMDD.P' format
    photos = ArrayField(models.URLField(), blank=True, default=list) 
 

    def clean(self):
        """Validate that input_date follows 'YYYYMMDD.P' format and extract values."""
        if self.input_date:
            try:
                # Split the input_date at the decimal point
                date_part, period_part = self.input_date.split('.')

                # Ensure the date part is 8 digits (YYYYMMDD) and the period part is valid
                if len(date_part) != 8 or not period_part.isdigit():
                    raise ValueError

                # Extract year, month, and day from the date_part
                self.tahun = int(date_part[:4])
                self.bulan = int(date_part[4:6])
                self.hari = int(date_part[6:8])

                # Extract the period as an integer
                self.periode = int(period_part)

                # Check if the extracted values are valid
                if not (1 <= self.bulan <= 12):
                    raise ValidationError("Bulan must be between 1 and 12.")
                if not (1 <= self.hari <= 31):
                    raise ValidationError("Hari must be between 1 and 31.")

            except (ValueError, IndexError):
                raise ValidationError("input_date must be in 'YYYYMMDD.P' format (e.g., '20240803.1').")

    def save(self, *args, **kwargs):
        """Automatically fill tahun, bulan, hari, and periode if input_date is provided and replace data if exists."""
        # If input_date exists, validate and populate the date fields
        if self.input_date:
            self.clean()

        # Check if a record with the same tmat_location, tahun, bulan, and periode exists
        existing_record = TMAT_LOCATION_DATA.objects.filter(
            tmat_location=self.tmat_location,
            tahun=self.tahun,
            bulan=self.bulan,
            periode=self.periode
        ).first()

        if existing_record:
            # Update the existing record's fields
            existing_record.hari = self.hari
            existing_record.nilai = self.nilai
            existing_record.save()
        else:
            # Call the parent class's save method if no existing record is found
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tmat_location.code} - {self.tahun}-{self.bulan}-{self.hari} - {self.periode}"

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(bulan__gte=1, bulan__lte=12), name='valid_bulan'),
            models.CheckConstraint(check=models.Q(hari__gte=1, hari__lte=31), name='valid_hari'),
        ]
        unique_together = ('tmat_location', 'tahun', 'bulan', 'periode')  # Ensure uniqueness for these fields
