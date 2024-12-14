from django.urls import path
from .views.dashboards.dashboards import MetabaseDashboards
from .views.dashboards.single import SingleDashboard, SingleDashboardByID
from .views.dashboards.shared import SharedDashboard
from .views.user.resend_invitation import MetabaseInvite
from .views.general import MetabaseURL

urlpatterns = [
    path("url/", MetabaseURL.as_view(), name="metabase_url"),
    path("public/dashboards/", MetabaseDashboards.as_view(), name="metabase_dashboard"),
    path("public/dashboards/single/", SingleDashboard.as_view(), name="metabase__single_dashboard"),
    path("public/dashboards/shared/", SharedDashboard.as_view(), name="metabase_shared_dashboard"),
    path("public/dashboards/<int:dashboard_id>/", SingleDashboardByID.as_view(), name="metabase_dashboard"),
    path("invite/",  MetabaseInvite.as_view(), name="metabase_invite"),
]
