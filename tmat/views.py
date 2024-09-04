from django.http import JsonResponse
from .models import TMAT_LOCATION_DATA



def tmat_location_data_chart(request):
    # Fetch data from the TMAT_LOCATION_DATA model
    code = request.GET.get('code', None) 
    queryset = TMAT_LOCATION_DATA.objects.select_related('tmat_location') 

    if code:
        queryset = queryset.filter(tmat_location__code=code)
    data = TMAT_LOCATION_DATA.objects.all().values('tahun', 'bulan', 'hari', 'nilai').order_by('tahun', 'bulan', 'hari')

    data = queryset.values('tahun', 'bulan', 'hari', 'nilai', 'tmat_location__code').order_by('tahun', 'bulan', 'hari')

    # Prepare data for the chart
    labels = []
    values = []
    codes = []  # To store location codes

    for entry in data:
        # Construct a label in 'YYYY-MM-DD' format
        date_label = f"{entry['tahun']}-{str(entry['bulan']).zfill(2)}-{str(entry['hari']).zfill(2)}"
        labels.append(date_label)
        values.append(entry['nilai'])
        codes.append(entry['tmat_location__code'])  # Append location code

    # Return data as JSON
    return JsonResponse({
        'labels': labels,  # Dates for the x-axis
        'values': values,  # Values for the y-axis
        'codes': codes,    # Location codes for the records
    })