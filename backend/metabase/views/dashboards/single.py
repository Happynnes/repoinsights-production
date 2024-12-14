from rest_framework.views import APIView
from django.http import JsonResponse

from ..connector.metabase_conn import MetabaseClient


class SingleDashboardByID(APIView):
    def post(self, request):
        dashboard_id = request.GET.get("id")
        client = MetabaseClient()
        dashboard = client.dashboard.get_dashboard_by_id(dashboard_id)
        return JsonResponse({"dashboard": dashboard}, safe=True)


class SingleDashboard(APIView):
    def post(self, request):
        user_id = request.user.id
        project_id = request.data.get("params")
        client = MetabaseClient()
        dashboards_ids = client.dashboard.get_dashboard_ids("single")
        iframes = client.dashboard.create_dashboard_response(dashboards_ids, user_id, project_id)
        return JsonResponse({"dashboards": iframes}, safe=True)
