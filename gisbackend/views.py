from django.http import JsonResponse
from .settings import ENV_URL




def TestURL(request):
    if ENV_URL == ".env":
        MODE = "Production"
    else:
        MODE = "Development"

    return JsonResponse ({
        "mode": MODE,
        "env": ENV_URL,
        "message": "Service is online",
        "version": "V1.3" })
