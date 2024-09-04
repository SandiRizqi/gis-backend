from django.http import JsonResponse
from django.db.models import Avg
from .models import TMAT_LOCATION_DATA



def tmat_location_data_chart(request):
    # Fetch data from the TMAT_LOCATION_DATA model
    code = request.GET.get('code', None) 
    queryset = TMAT_LOCATION_DATA.objects.select_related('tmat_location')

    if code:
        queryset = queryset.filter(tmat_location__code=code)
    
    # Group data by year, month, and day and calculate the average 'nilai' for each group
    data = queryset.values('tahun', 'bulan', 'hari', 'tmat_location__code')\
                   .annotate(average_nilai=Avg('nilai'))\
                   .order_by('tahun', 'bulan', 'hari')

    # Prepare data for the chart
    labels = []
    values = []
    codes = []  # To store location codes
    total_values = []

    for entry in data:
        # Construct a label in 'YYYY-MM-DD' format
        date_label = f"{entry['tahun']}-{str(entry['bulan']).zfill(2)}-{str(entry['hari']).zfill(2)}"
        labels.append(date_label)
        values.append(entry['average_nilai'])  # Append average value for the day
        codes.append(entry['tmat_location__code'])  # Append location code
        total_values.append(entry['average_nilai'])  # Track the same values for averaging

    # Calculate the overall average of the `values`
    overall_average = sum(values) / len(values) if values else 0
    averages = [overall_average] * len(values)  # Repeat the overall average for each entry

    # Return data as JSON
    return JsonResponse({
        'labels': labels,   # Dates for the x-axis
        'values': values,   # Average values for the y-axis
        'codes': codes,     # Location codes for the records
        'averages': averages  # Overall average repeated for each entry
    })