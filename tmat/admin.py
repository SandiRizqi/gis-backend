import csv
from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path
from django.contrib import messages
from django.http import HttpResponse
from .models import TMAT_LOCATIONS
from .forms import TMATLocationsCSVUploadForm
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSGeometry
import json

class TMAT_LOCATIONSAdmin(admin.ModelAdmin):
    list_display = ('code', 'werks', 'afd_name', 'block_name', 'no', 'soil', 'longitude', 'latitude')
    search_fields = ('code', 'afd_name', 'block_name', 'no')
    list_filter = ('werks', 'afd_name', 'block_name', 'soil')
    readonly_fields = ('geom',)
    change_list_template = "admin/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='upload_csv'),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "Please upload a valid CSV file.")
                return redirect("admin:upload_csv")

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                
                # Skip the header row
                next(reader)

                for row in reader:
                    if len(row) != 8:
                        messages.error(request, f"Row has an unexpected number of values: {row}")
                        continue

                    code, werks, afd_name, block_name, no, soil, longitude, latitude = row
                    feature = {
                                "type": "Point",
                                "coordinates": [float(longitude), float(latitude)]
                            }
                    geom = GEOSGeometry(json.dumps(feature))

                    # Update or create TMAT_LOCATIONS object
                    TMAT_LOCATIONS.objects.update_or_create(
                        code=code,
                        defaults={
                            'werks': int(werks),
                            'afd_name': afd_name,
                            'block_name': block_name,
                            'no': no,
                            'soil': soil,
                            'longitude': longitude,
                            'latitude': latitude,
                            'geom': geom
                        }
                    )
                
                messages.success(request, "CSV file uploaded and data imported successfully.")
            except Exception as e:
                messages.error(request, f"Error uploading CSV: {str(e)}")
            return redirect("admin:upload_csv")

        form = TMATLocationsCSVUploadForm()
        context = {
            'form': form,
            'title': 'Upload CSV File',
            'opts': self.model._meta
        }
        return render(request, "admin/upload_csv.html", context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['upload_csv_url'] = 'upload-csv/'  # URL for CSV upload
        return super(TMAT_LOCATIONSAdmin, self).changelist_view(request, extra_context=extra_context)

admin.site.register(TMAT_LOCATIONS, TMAT_LOCATIONSAdmin)
