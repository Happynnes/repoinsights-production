from rest_framework.views import APIView
from django.http import JsonResponse

from .helper.variables import metric_scores as metric_scores
from .helper.project_manager import ProjectManager
from .helper.metric_score import ProjectMetricScore
from .helper.filter_data_manager import FilterDataManager


class WeightError(Exception):
    pass


class RepoInsightsFeaturedProjects(APIView):
    @staticmethod
    def validate_weights():
        if sum(metric["weight"]["value"] for metric in metric_scores) != 1.0:  # type: ignore
            raise WeightError("Metric weights must sum to 1.0")

    def invert_if_necessary(self, metric, numeric_rating):
        if metric["weight"]["invert"] is True:
            return 1 - numeric_rating
        return numeric_rating

    def find_numeric_rating(self, metric_id, projects):
        for project in projects["rating"]:
            if project["id"] == metric_id:
                return project["value"]
        return None

    def calculate_score(self, metrics_scores, projects):
        score = 0
        for metric in metrics_scores:
            metric_name = metric["name"]
            numeric_rating = self.find_numeric_rating(metric_name, projects)
            if numeric_rating is not None:
                numeric_rating = self.invert_if_necessary(metric, numeric_rating)
                score += metric["weight"]["value"] * numeric_rating
        return score

    def get_top_n_repos(self, metrics_scores, projects, n):
        for project in projects:
            project["score"] = self.calculate_score(metrics_scores, project)
        sorted_repos = sorted(projects, key=lambda x: x["score"], reverse=True)
        return sorted_repos[:n]

    def get(self, request):
        number_of_projects: int = request.GET.get("top", 3)
        current_user_id = request.user.id
        try:
            self.validate_weights()
            projects = ProjectManager.get_projects()
            projects = ProjectMetricScore.calc_metric_score(list(projects))
            top_projects = self.get_top_n_repos(
                metric_scores, projects, number_of_projects
            )

            user_project_ids = ProjectManager.get_user_selected_project_ids(
                current_user_id
            )
            top_projects = FilterDataManager.user_selected(
                top_projects, user_project_ids
            )
            return JsonResponse({"projects": top_projects}, status=200, safe=True)

        except WeightError as e:
            return JsonResponse({"error": str(e)}, status=500)
