from pprint import pprint
from django.http import JsonResponse
from rest_framework.views import APIView
from ..models import Project, Commit

from django.db.models import Count, F, Max, Subquery, OuterRef
from .helper.variables import LANGS, COMMIT, USER, SORT
from .helper.filter_data_manager import FilterDataManager
from .helper.project_manager import ProjectManager
from .helper.metric_score import ProjectMetricScore


class RepoInsightsExplore(APIView):
    def get(self, request):
        user = request.user
        current_user_id = user.id
        req_langs = request.GET.get(LANGS)
        req_commits = request.GET.get(COMMIT)
        req_user = request.GET.get(USER)

        private_projects_ids = ProjectManager.get_private_projects_ids(user)
        projects = ProjectManager.get_projects(
            extra_condition={"id__in": private_projects_ids}
        )
        print(private_projects_ids)

        if req_user:
            if req_user == "Proyectos seleccionados":
                user_project_ids = list(
                    ProjectManager.get_user_selected_project_ids(current_user_id)
                )
                projects = projects.filter(id__in=user_project_ids)

            elif req_user == "Proyectos privados":
                ids = list(private_projects_ids)
                projects = projects.filter(id__in=ids)

            else:
                return JsonResponse({"error": "Invalid user filter"}, status=500)

        if req_langs:
            req_langs = req_langs.split(",")
            projects = projects.filter(language__in=req_langs)

        if req_commits:
            commits_list: list = req_commits.split(",")
            for commit in commits_list:
                min_limit, max_limit = FilterDataManager.get_intervals(commit)
                projects = FilterDataManager.project_filtered_by_commits(
                    projects, min_limit, max_limit
                )

        result = ProjectMetricScore.calc_metric_score(list(projects))
        total = len(result)
        user_project_ids = ProjectManager.get_user_selected_project_ids(current_user_id)
        result = FilterDataManager.user_selected(result, user_project_ids)

        response = {"data": result, "total": total}
        return JsonResponse(response, safe=True)


class RepoInsightsExploreProject(APIView):
    def get(self, request, project_id):
        projects = list(ProjectManager.get_project_by_id(project_id))
        if len(projects) == 0:
            return JsonResponse({"error": "Project not found"}, status=404)
        if len(projects) > 1:
            return JsonResponse({"error": "Multiple projects found"}, status=500)
        if len(projects) == 1 and projects[0]["private"]:
            single_project = projects[0]
            user = request.user
            private_projects_ids = ProjectManager.get_private_projects_ids(user)
            if single_project["id"] not in private_projects_ids:
                return JsonResponse({"error": "Private repository"}, status=404)
        projects = ProjectMetricScore.calc_metric_score(projects)
        user_projects = ProjectManager.get_user_selected_project_ids(request.user.id)
        project = list(projects)[0]
        project["selected"] = True if project_id in user_projects else False
        return JsonResponse(project, safe=True)
