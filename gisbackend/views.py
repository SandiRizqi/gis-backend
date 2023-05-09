from django.http import HttpResponse, JsonResponse



def TestURL(request):
    HttpResponse ({"message": "POST Successfully" }, status=201)