from django.http import JsonResponse
from .models import TMAT_LOCATION_DATA



def tmat_location_data_chart(request):
    # Fetch data from the TMAT_LOCATION_DATA model
    data = TMAT_LOCATION_DATA.objects.all().values('tahun', 'bulan', 'hari', 'nilai').order_by('tahun', 'bulan', 'hari')

    # Prepare data for the chart
    labels = []
    values = []
    
    for entry in data:
        # Construct a label in 'YYYY-MM-DD' format
        date_label = f"{entry['tahun']}-{str(entry['bulan']).zfill(2)}-{str(entry['hari']).zfill(2)}"
        labels.append(date_label)
        values.append(entry['nilai'])

    # Return data as JSON
    return JsonResponse({
        'labels': labels,  # Dates for the x-axis
        'values': values,  # Values for the y-axis
    })
