from django.http import HttpResponse, JsonResponse



def TestURL(request):
    return HttpResponse ({"message": "POST Successfully" }, status=201)
