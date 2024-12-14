from django.shortcuts import render
from rest_framework.views import APIView
from .models import UserRepoInsightProject
from django.http import JsonResponse

class UserRepoInsightsProjects(APIView):
    def post(self, request):
        if request.data is None:
            return JsonResponse({"success": False, "error": "No data provided"}, status=400)

        project_id = request.data.get("project_id")
        action = request.data.get("action")
        current_user_id = request.user.id

        if action not in ["add", "remove"]:
            return JsonResponse({"success": False, "error": "Invalid action"}, status=400)

        if action == "add":
            user_repo_insight_project = UserRepoInsightProject.objects.create(
                user_id=current_user_id,
                repoinsight_project_id=project_id
            )
        else:
            UserRepoInsightProject.objects.filter(
                user_id=current_user_id,
                repoinsight_project_id=project_id
            ).delete()

        return JsonResponse({"success": True, "action": action}, status=200)
