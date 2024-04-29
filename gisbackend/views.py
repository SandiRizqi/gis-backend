from django.http import JsonResponse, HttpResponse
from .settings import ENV_URL


def TestURL(request):
    if ENV_URL == ".env":
        MODE = "Production"
    else:
        MODE = "Development"

    #update_deforestations()

    return JsonResponse ({
        "mode": MODE,
        "env": ENV_URL,
        "message": "Service is online",
        "version": "V2.9" })