import csv
from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path
from django.contrib import messages
from django.http import HttpResponse
from .models import TMAT_LOCATIONS, TMAT_LOCATION_DATA
from .forms import TMATLocationsCSVUploadForm, TMATLocationDataCSVUploadForm
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from django.db import IntegrityError
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
    



class TMAT_LOCATION_DATAAdmin(admin.ModelAdmin):
    list_display = ('tmat_location', 'input_date', 'tahun', 'bulan', 'hari', 'periode', 'nilai')
    search_fields = ('tmat_location__code', 'input_date')
    list_filter = ('periode', 'tahun', 'bulan')
    readonly_fields = ('tahun', 'bulan', 'hari', 'periode')  # These fields will be auto-filled

    change_list_template = "admin/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='upload_tmat_location_data_csv'),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "Please upload a valid CSV file.")
                return redirect("admin:upload_tmat_location_data_csv")

            # Read and process the CSV file
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)

                # Skip the header row
                next(reader)

                for row in reader:
                    try:
                        # Parse the CSV row into variables
                        code, input_date, nilai = row

                        # Fetch the TMAT_LOCATIONS object using the code from the CSV
                        try:
                            tmat_location = TMAT_LOCATIONS.objects.get(code=code)
                        except TMAT_LOCATIONS.DoesNotExist:
                            messages.error(request, f"TMAT_LOCATION with code {code} does not exist.")
                            continue

                        # Create TMAT_LOCATION_DATA object
                        tmat_location_data = TMAT_LOCATION_DATA(
                            tmat_location=tmat_location,
                            input_date=input_date,
                            nilai=int(nilai) if nilai else None
                        )

                        # Automatically fill in the year, month, day, and period from input_date
                        tmat_location_data.clean()

                        # Save the instance
                        tmat_location_data.save()

                    except ValidationError as e:
                        messages.error(request, f"Validation error for code {code}: {str(e)}")
                    except IntegrityError as e:
                        messages.error(request, f"Integrity error for code {code}: {str(e)}")
                    except Exception as e:
                        messages.error(request, f"Error processing code {code}: {str(e)}")

                messages.success(request, "CSV file uploaded and data imported successfully.")
            except Exception as e:
                messages.error(request, f"Error uploading CSV: {str(e)}")
            return redirect("admin:upload_tmat_location_data_csv")

        form = TMATLocationDataCSVUploadForm()
        context = {
            'form': form,
            'title': 'Upload TMAT Location Data CSV File',
            'opts': self.model._meta
        }
        return render(request, "admin/upload_csv.html", context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['upload_csv_url'] = 'upload-csv/'
        return super(TMAT_LOCATION_DATAAdmin, self).changelist_view(request, extra_context=extra_context)
    
    

admin.site.register(TMAT_LOCATION_DATA, TMAT_LOCATION_DATAAdmin)
admin.site.register(TMAT_LOCATIONS, TMAT_LOCATIONSAdmin)
