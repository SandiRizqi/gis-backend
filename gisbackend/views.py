from django.http import JsonResponse, HttpResponse
from .settings import ENV_URL
from api.task import test_func

def TestURL(request):
    if ENV_URL == ".env":
        MODE = "Production"
    else:
        MODE = "Development"

    return JsonResponse ({
        "mode": MODE,
        "env": ENV_URL,
        "message": "Service is online",
<<<<<<< HEAD
        "version": "V1.7" })

=======
        "version": "V1.5" })

def Task(request):
    test_func.delay()
    return HttpResponse("Done")
>>>>>>> 69d4217 (update)
