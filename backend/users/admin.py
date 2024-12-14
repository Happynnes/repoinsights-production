from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserRepoInsightProject


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Github Info",
            {
                "fields": (
                    "github_id",
                    "github_username",
                    "github_email",
                    "github_avatar_url",
                    "github_access_token",
                    "github_url",
                    "github_bio",
                    "github_company",
                    "github_location",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserRepoInsightProject)