from django.db.models import F
from django.http import JsonResponse
from rest_framework.views import APIView

from .helper.project_manager import ProjectManager
from .helper.metric_score import ProjectMetricScore
from .helper.filter_data_manager import FilterDataManager


class RepoInsightsProjects(APIView):
    def get(self, request):
        user_id = request.user.id
        projects = list(ProjectManager.get_projects())
        languages = list(ProjectManager.get_languages())
        user_projects = list(ProjectManager.get_user_selected_project_ids(user_id))
        projects = FilterDataManager.user_selected(projects, user_projects)

        response = {
            "projects": {"data": projects, "total": len(projects)},
            "languages": {"data": languages, "total": len(languages)},
        }
        return JsonResponse(response, safe=True)


class RepoInsightsFavProjects(APIView):
    def get(self, request):
        print(request.GET)
        response = {}
        current_user = request.user
        user_id = current_user.id
        add_metrics = request.GET.get("metrics", True)
        user_projects_ids = ProjectManager.get_user_selected_project_ids(user_id)

        projects = ProjectManager.get_user_selected_projects(current_user)

        projects = list(projects)
        projects = FilterDataManager.user_selected(projects, user_projects_ids)

        if add_metrics:
            projects = ProjectMetricScore.calc_metric_score(
                projects, show_empty_values=True
            )
            metrics = ProjectMetricScore.get_metrics()
            response["metrics"] = metrics

        response["projects"] = projects
        return JsonResponse(response, safe=True)
