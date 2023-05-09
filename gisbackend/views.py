from django.http import HttpResponse, JsonResponse



def TestURL(request):
    return JsonResponse ({"message": "POST Successfully" })
