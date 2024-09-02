# admin.py
import csv
from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path
from django.http import HttpResponse
from django.contrib import messages
from .models import TMAT_LOCATIONS
from .forms import TMATLocationsCSVUploadForm
from django.contrib.gis.geos import Point

class TMAT_LOCATIONSAdmin(admin.ModelAdmin):
    list_display = ('code', 'werks', 'afd_name', 'block_name', 'no', 'soil', 'longitude', 'latitude')
    search_fields = ('code', 'afd_name', 'block_name', 'no')
    list_filter = ('werks', 'afd_name', 'block_name', 'soil')
    readonly_fields = ('geom',)

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

            # Read and process the CSV file
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)

                # Skip the header row
                next(reader)

                for row in reader:
                    code, werks, afd_name, block_name, no, soil, longitude, latitude = row
                    geom = Point(float(longitude), float(latitude), srid=4326)

                    # Create TMAT_LOCATIONS object
                    TMAT_LOCATIONS.objects.create(
                        code=code,
                        werks=int(werks),
                        afd_name=afd_name,
                        block_name=block_name,
                        no=no,
                        soil=soil,
                        longitude=longitude,
                        latitude=latitude,
                        geom=geom
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
        return HttpResponse(render(request, "admin/upload_csv.html", context))

admin.site.register(TMAT_LOCATIONS, TMAT_LOCATIONSAdmin)
