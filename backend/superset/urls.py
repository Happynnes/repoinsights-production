from django.urls import path
from .views import get_dashboard_guest_token, ContributorsSuperset, HeatmapSuperset, ExtraInformationSuperset, DailyCommits3D, DailyIssues3D, DailyPRsMerged3D, DailyPRsClosed3D

urlpatterns = [
    path('get-dashboard-guest-token/<int:dashboard_id>/', get_dashboard_guest_token, name='get_dashboard_guest_token'),
    path("getTopContributors/", ContributorsSuperset.as_view(), name="topContributors"),
    path("getHeatmap/", HeatmapSuperset.as_view(), name="heatmap"),
    path("getExtraInfo/", ExtraInformationSuperset.as_view(), name="extraInfo"),
    path("get3dInfo/", DailyCommits3D.as_view(), name="3dInfo"),
    path("get3dInfoIssues/", DailyIssues3D.as_view(), name="3dInfoIssues"),
    path("get3dInfoPRs/", DailyPRsMerged3D.as_view(), name="3dInfoPRs"),
    path("get3dInfoPRsClosed/", DailyPRsClosed3D.as_view(), name="3dInfoPRsClosed"),
]
