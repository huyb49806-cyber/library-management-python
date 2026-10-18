from django.http import JsonResponse


def home(request):
    return JsonResponse({"service": "library-management", "status": "ok"})
