
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import path
from tmat.models import TMAT_LOCATION_DATA
from django.db.models import Q

@staff_member_required
def admin_statistics_view(request):
    return render(request, "admin/statistics.html", {
        "title": "Statistics"
    })


@staff_member_required
def tmat_statistics_view(request):
    # Get filter parameters
    selected_year = request.GET.get('tahun', '')
    selected_month = request.GET.get('bulan', '')
    selected_period = request.GET.get('periode', '')

    # Build query based on filters
    filters = Q()
    if selected_year:
        filters &= Q(tahun=selected_year)
    if selected_month:
        filters &= Q(bulan=selected_month)
    if selected_period:
        filters &= Q(periode=selected_period)

    # Apply filters to query
    data_list = TMAT_LOCATION_DATA.objects.select_related('tmat_location').filter(filters)

    # Get filter options
    years = TMAT_LOCATION_DATA.objects.values_list('tahun', flat=True).distinct().order_by('tahun')
    months = TMAT_LOCATION_DATA.objects.values_list('bulan', flat=True).distinct().order_by('bulan')
    periods = TMAT_LOCATION_DATA.objects.values_list('periode', flat=True).distinct().order_by('periode')

    return render(request, "admin/tmat_map.html", {
        "title": "TMAT",
        "data_list": data_list,
        "years": years,
        "months": months,
        "periods": periods,
        "selected_year": selected_year,
        "selected_month": selected_month,
        "selected_period": selected_period
    })




class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request, _=None):
        app_list = super().get_app_list(request)
        app_list += [
            {
                "name": "Dashboard",
                "app_label": "my_dashboard",
                "models": [
                    {
                        "name": "Hotspot_Statistic",
                        "object_name": "hotspot_statistics",
                        "admin_url": "/admin/statistics",
                        "view_only": True,
                    },
                    {
                        "name": "TMAT",
                        "object_name": "tmat",
                        "admin_url": "/admin/tmatmap",
                        "view_only": True,
                    }
                ],
            }
        ]
        return app_list

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            path("statistics/", admin_statistics_view, name="admin-statistics"),
            path("tmatmap/", tmat_statistics_view, name="tmat-statistics"),
        ]
        return urls