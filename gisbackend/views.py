from django.http import JsonResponse, HttpResponse
from .settings import ENV_URL
from api.tasks import update_deforestations
from api.task import test_func

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
        "version": "V1.9" })


def Task(request):
    test_func.delay()
    return HttpResponse("Done")
