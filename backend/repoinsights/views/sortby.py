from rest_framework.views import APIView
from django.http import JsonResponse

from .helper.metric_score import ProjectMetricScore


class RepoInsightsSort(APIView):
    def get(self, request):
        metrics = ProjectMetricScore.get_metrics()
        return JsonResponse({"metrics": metrics}, safe=True)
