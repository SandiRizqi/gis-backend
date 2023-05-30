from django.http import JsonResponse
from .settings import env




def TestURL(request):
    return JsonResponse ({
        "mode": env.get('MODE'),
        "message": "Service is online",
        "version": "V1.3" })
