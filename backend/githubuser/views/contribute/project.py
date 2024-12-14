from rest_framework.views import APIView
import requests
from datetime import datetime
from urllib.parse import urlparse
from django.http import JsonResponse

from rabbitmq.connector import QueueController
from rabbitmq.utils import format_dt

from repoinsights.views.helper.project_manager import ProjectManager

class GitHubContribute(APIView):
    def get_owner_and_repo(self, github_url):
        url = urlparse(github_url)
        path = url.path.split("/")
        owner = path[1]
        repo = path[2]
        return owner, repo
    

    
    def post(self, request):
        current_user = request.user.id
        github_url = request.data.get("url")
        try:
            owner, repo = self.get_owner_and_repo(github_url)
            exists = ProjectManager.check_if_project_exists(owner, repo)
            if exists:
                return JsonResponse({"error": "Project already exists"}, safe=True, status=400)
        except:
            return JsonResponse({"error": "Invalid GitHub URL"}, safe=True, status=400)

        project_message = {
                "enqueue_time": format_dt(datetime.now()),
                "attempt": 1,
                "owner": owner,
                "project": repo,
                "last_extraction": None,
            }
        queue_controller = QueueController()
        queue_controller.connect()
        queue_controller.enqueue(project_message)

        return JsonResponse({"success": "Contribution request sent"}, safe=True, status=200)