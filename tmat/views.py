from django.http import JsonResponse
from django.db.models import Avg
from .models import TMAT_LOCATION_DATA
from django.db.models import Count, Case, When, IntegerField



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


def tmat_location_percentage_data_chart(request):
    # Group data by year, month, and period, and calculate the total and count of nilai > -40
    data = TMAT_LOCATION_DATA.objects.values('tahun', 'bulan', 'periode')\
        .annotate(
            total_records=Count('id'),  # Total records in each group
            count_greater_than_40=Count(
                Case(
                    When(nilai__gt=-40, then=1),
                    output_field=IntegerField()
                )
            )
        ).order_by('tahun', 'bulan', 'periode')

    # Prepare data structure for each year
    results_by_year = {}
    all_labels = set()  # To store all unique labels (MM-PP)
    years = set()  # To store distinct years

    for entry in data:
        year = entry['tahun']
        years.add(year)  # Add the year to the set of distinct years

        # Generate label as 'MM-PP' (month-period)
        label = f"{entry['bulan']:02d}-{entry['periode']:02d}"
        all_labels.add(label)  # Add the label to the set of all labels

        # If this is the first time encountering this year, create the structure
        if year not in results_by_year:
            results_by_year[year] = {}

        # Calculate percentage
        percentage = (entry['count_greater_than_40'] / entry['total_records']) * 100 if entry['total_records'] else None

        # Store percentage for the specific label, use `None` instead of 0
        results_by_year[year][label] = percentage

    # Convert the set of years and labels to sorted lists
    years_list = sorted(list(years))
    sorted_labels = sorted(list(all_labels))

    # Prepare datasets with missing labels filled with `null` (None in Python)
    datasets = []
    for year in years_list:
        year_data = []
        for label in sorted_labels:
            # Use the percentage if it exists, otherwise use `None` to break the line
            year_data.append(results_by_year[year].get(label, None))
        
        datasets.append({
            'label': str(year),  # Use the year as the dataset label
            'data': year_data,  # Percentages as data points (with `None` for missing labels)
            'borderColor': f'rgba({(year * 37) % 256}, {(year * 71) % 256}, {(year * 93) % 256}, 1)',  # Unique color per year
            'borderWidth': 2,
            'fill': False
        })

    # Return data as JSON for Chart.js
    return JsonResponse({
        'labels': sorted_labels,  # All labels (MM-PP)
        'datasets': datasets  # Multiple datasets for each year
    })