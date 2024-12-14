from django.db.models import Max, F, Q
from typing import Optional
from ...models import Project, Commit
from users.models import UserRepoInsightProject

class ProjectManager:
    @staticmethod
    def get_user_selected_project_ids(current_user_id: int):
        projects = UserRepoInsightProject.objects.filter(user_id=current_user_id).values_list(
            "repoinsight_project_id", flat=True
        )
        return projects

    @staticmethod
    def get_user_selected_projects(current_user):
        current_user_id = current_user.id
        user_project_ids = list(ProjectManager.get_user_selected_project_ids(current_user_id))
        user_private_ids = list(ProjectManager.get_private_projects_ids(current_user))
        user_projects = user_project_ids + user_private_ids
        projects = (
            Project.objects.using("repoinsights")
            .filter(forked_from__isnull=True, deleted=False)
            .annotate(
                last_extraction_date=Max("extractions__date"),
                owner_name=F("owner__login")
            )
            .values("id", "name", "language", "owner_name", "last_extraction_date", "created_at")
            .filter(id__in=user_projects)
        )
        return projects

    @staticmethod
    def get_private_projects_ids(user):
        github_user_name = user.github_username
        project_ids = Project.objects.using("repoinsights").filter(owner__login=github_user_name, private=True).values_list(
            "id", flat=True
        )
        return project_ids
        

    @staticmethod
    def get_projects(extra_condition: Optional[dict] = None):
        if extra_condition is None:
            extra_condition = {}
        
        if "id__in" in extra_condition:
            condition = Q(private=False) | Q(id__in=extra_condition["id__in"])
        else:
            condition = Q(private=False)

        projects = (
            Project.objects.using("repoinsights")
            .filter(
            condition,
            forked_from__isnull=True, 
            deleted=False
            )
            .annotate(
                last_extraction_date=Max("extractions__date"),
                owner_name=F("owner__login")
            )
            .values("id", "name", "owner_name", "last_extraction_date", "language", "created_at", "private")
            .distinct()
            .order_by("-last_extraction_date")
        )
                
        return projects


    @staticmethod    
    def get_project_by_id(id):
        project = (
            Project.objects.using("repoinsights")
            .filter(id=id)
            .annotate(
                last_extraction_date=Max("extractions__date"),
                owner_name=F("owner__login")
            )
            .values("id", 
                    "name", 
                    "owner_name", 
                    "last_extraction_date", 
                    "language", 
                    "created_at", 
                    "description",
                    "private",
                    "url"
                    )
            .distinct()
        )
        return project


    @staticmethod
    def get_languages():
        languages = list(
            Project.objects.using("repoinsights")
            .filter(forked_from__isnull=True, deleted=False)
            .values_list("language", flat=True)
            .distinct()
        )
        return languages
    
    @staticmethod
    def check_if_project_exists(owner: str, project_name: int):
        # find project_name in Projects and owner is in Users.login
        project = (
            Project.objects.using("repoinsights")
            .filter(name=project_name, owner__login=owner)
            .values("id")
        )
        return project.exists()
