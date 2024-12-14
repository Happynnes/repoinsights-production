from rest_framework.views import APIView
from django.http import JsonResponse
from django.conf import settings

class MetabaseURL(APIView):
    def get(self, request):
        return JsonResponse({"url": settings.METABASE_URL}, status=200)
