from django.http import HttpResponse, JsonResponse



def TestURL(request):
    return JsonResponse ({"message": "Service is online",
                          "version": "V1.0" })
