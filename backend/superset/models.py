from django.db import models
from users.models import CustomUser

class SupersetUserData(models.Model):
    user = models.OneToOneField(CustomUser, related_name="supersetuser", on_delete=models.CASCADE)  # type: ignore
    superset_user_id = models.IntegerField(null=False, blank=False)
    superset_group_id = models.IntegerField(null=False, blank=False, default=-1)
    superset_db_id = models.IntegerField(null=False, blank=False, default=-1)

    def __str__(self):
        return f"{self.user.username} - Superset User ID: {self.superset_user_id}"
