from rest_framework.views import APIView
from django.http import JsonResponse

from ..connector.metabase_conn import MetabaseClient


class SharedDashboard(APIView):
    def post(self, request):
        user_id = request.user.id
        project_id = request.data.get("params")
        client = MetabaseClient()
        dashboards_ids = client.dashboard.get_dashboard_ids("shared")
        iframes = client.dashboard.create_dashboard_response(dashboards_ids, user_id, project_id)
        return JsonResponse({"dashboards": iframes}, safe=True)
