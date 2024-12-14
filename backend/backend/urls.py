from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/metabase/", include("metabase.urls")),
    path("api/social/", include("social.urls")),
    path("api/repoinsights/", include("repoinsights.urls")),
    path("api/github/", include("githubuser.urls")),
    path("api/user/", include("users.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/superset/", include("superset.urls")),
]
