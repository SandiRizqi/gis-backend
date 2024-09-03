
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import path
from tmat.models import TMAT_LOCATION_DATA

@staff_member_required
def admin_statistics_view(request):
    return render(request, "admin/statistics.html", {
        "title": "Statistics"
    })


@staff_member_required
def tmat_statistics_view(request):
    data_list = TMAT_LOCATION_DATA.objects.select_related('tmat_location').all()
    return render(request, "admin/tmat_map.html", {
        "title": "TMAT",
        "data_list": data_list
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