from django.http import JsonResponse
import os




def TestURL(request):
    MODE = os.environ["ENVMODE"]

    return JsonResponse ({
        "mode": MODE,
        "message": "Service is online",
        "version": "V1.3" })
