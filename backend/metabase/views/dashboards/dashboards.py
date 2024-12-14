from pprint import pprint
from typing import Any, Tuple
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
import jwt
import time
from django.conf import settings

from repoinsights.views.helper.project_manager import ProjectManager
from metabase.views.connector.metabase_conn import MetabaseClient


class MetabaseDashboards(APIView):
    def __init__(self) -> None:
        self.METABASE_SITE_URL = settings.METABASE_URL
        self.METABASE_SECRET_KEY = settings.METABASE_SECRET_KEY

    def get_token(self, payload):
        return jwt.encode(payload, self.METABASE_SECRET_KEY, algorithm="HS256")

    def get_ids(self):
        client = MetabaseClient()
        dashboard_ids = client.dashboard.get_dashboard_ids()
        return dashboard_ids

    def create_iframe_url(self, user_id, dashboard_id, params) -> Tuple:
        if params is None:
            project_ids = ProjectManager.get_user_selected_project_ids(user_id)
            project_ids = [str(project_id) for project_id in project_ids]
            params = {"id": project_ids}

        payload = {
            "resource": {"dashboard": int(dashboard_id)},
            "params": params,
            "exp": round(time.time()) + (60 * 10),
        }

        iframeUrl = (
            self.METABASE_SITE_URL
            + "/embed/dashboard/"
            + self.get_token(payload)
            + "#bordered=true&titled=true"
        )
        return iframeUrl, params

    def post(self, request):
        iframes = []
        user_id = request.user.id
        params = request.data.get("params", None)
        for dashboard in self.get_ids():
            iframe, params = self.create_iframe_url(user_id, dashboard["id"], params)
            iframes.append({"iframe": iframe, "params": params})

        return JsonResponse({"iframes": iframes}, safe=True)
