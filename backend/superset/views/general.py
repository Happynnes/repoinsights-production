from rest_framework.views import APIView
from django.http import JsonResponse
from django.conf import settings

class SupersetURL(APIView):
    def get(self, request):
        return JsonResponse({"url": settings.SUPERSET_URL}, status=200)
