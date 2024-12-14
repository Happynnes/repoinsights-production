from django.urls import path
from repoinsights.views.explore import RepoInsightsExplore, RepoInsightsExploreProject
from repoinsights.views.filters import RepoInsightsProjectsFilters
from repoinsights.views.projects import RepoInsightsProjects
from repoinsights.views.projects import RepoInsightsFavProjects
from repoinsights.views.featured import RepoInsightsFeaturedProjects
from repoinsights.views.sortby import RepoInsightsSort
from repoinsights.views.summary_metrics import RepoInsightsSummaryMetrics

urlpatterns = [
    path("projects/", RepoInsightsProjects.as_view(), name="get_all_projects"),
    path("projects/favorites/", RepoInsightsFavProjects.as_view(), name="get_all_projects_favorites"),
    path("filters/", RepoInsightsProjectsFilters.as_view(), name="get_all_projects_filters"),
    path("summary/", RepoInsightsSummaryMetrics.as_view(), name="summary_metrics"),
    path("sort/", RepoInsightsSort.as_view(), name="get_all_projects_sort"),
    path("explore/", RepoInsightsExplore.as_view(), name="explore_projects"),
    path("explore/<int:project_id>/", RepoInsightsExploreProject.as_view(), name="explore_project"),
    path("explore/featured/", RepoInsightsFeaturedProjects.as_view(), name="explore_featured_projects"),
]
