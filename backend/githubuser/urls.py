from django.urls import path, include
from .views.views import (
    GitHubProjects,
    UserTokens,
    GitHubAddProject,
    UserAddTokens,
    GitHubCheckPrivate,
)
from .views.contribute.project import GitHubContribute

urlpatterns = [
    path("projects/", GitHubProjects.as_view(), name="github_projects"),
    path("projects/check-private/", GitHubCheckPrivate.as_view(), name="check_private"),
    path("projects/add", GitHubAddProject.as_view(), name="github_projects_add"),
    path("contribute/", GitHubContribute.as_view(), name="github_contribute"),
    path("tokens/", UserTokens.as_view(), name="github_token"),
    path("tokens/add", UserAddTokens.as_view(), name="github_token_add"),
]
