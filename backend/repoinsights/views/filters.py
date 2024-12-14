from django.http import JsonResponse
from rest_framework.views import APIView

from .helper.variables import LANGS, COMMIT, USER, PERSONAL
from .helper.filter_data_manager import FilterDataManager
from .helper.project_manager import ProjectManager
from repoinsights.models import Project


class RepoInsightsProjectsFilters(APIView):
    def get(self, request):
        user_filter = request.GET.get(USER)
        langs_filter = request.GET.get(LANGS)
        commits_filter = request.GET.get(COMMIT)
        current_user = request.user
        current_user_id = current_user.id
        response = {}

        filter_data = {
            LANGS: {
                "title": "Lenguajes",
                "key": LANGS,
            },
            USER: {
                "title": "Usuario",
                "key": USER,
            },
            COMMIT: {
                "title": "Commits",
                "key": COMMIT,
            },
        }

        if USER in filter_data.keys():
            if current_user_id is None:
                JsonResponse({"error": "No user id found"}, status=500)

            user_project_ids = list(
                ProjectManager.get_user_selected_project_ids(current_user_id)
            )
            user_private_project_ids = ProjectManager.get_private_projects_ids(
                current_user
            )
            response[USER] = {
                "data": [
                    {"name": "Proyectos seleccionados", "count": len(user_project_ids)},
                    {
                        "name": "Proyectos privados",
                        "count": len(user_private_project_ids),
                    },
                ],
                "info": filter_data[USER],
            }

        if LANGS in filter_data.keys():
            if user_filter:
                user_project_ids = list(
                    ProjectManager.get_user_selected_project_ids(current_user_id)
                )
                projects = ProjectManager.get_projects().filter(id__in=user_project_ids)
            else:
                projects = Project.objects.using("repoinsights").filter(
                    forked_from__isnull=True,
                    deleted=False,
                    private=False,
                    language__isnull=False,
                )

            commits = commits_filter.split(",") if commits_filter else None
            if commits:
                for commit in commits:
                    min_limit, max_limit = FilterDataManager.get_intervals(commit)
                    projects = FilterDataManager.get_projects_by_commits(
                        projects, min_limit, max_limit
                    )
            langs_with_counts = FilterDataManager.get_languages(projects)
            langs = [
                {"name": lang["language"], "count": lang["total"]}
                for lang in langs_with_counts
            ]
            response[LANGS] = {
                "data": langs,
                "total": len(langs),
                "info": filter_data[LANGS],
            }
        if COMMIT in filter_data.keys():
            user_project_ids = (
                list(ProjectManager.get_user_selected_project_ids(current_user_id))
                if user_filter
                else []
            )
            langs = langs_filter.split(",") if langs_filter else []
            data = FilterDataManager.get_commits_data(user_project_ids, langs)

            response[COMMIT] = {
                "data": data,
                "total": len(data),
                "info": filter_data[COMMIT],
            }
        return JsonResponse(response, safe=True)
