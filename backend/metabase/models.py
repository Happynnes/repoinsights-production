from django.db import models
from users.models import CustomUser


class MetabaseUserData(models.Model):
    user = models.OneToOneField(CustomUser, related_name="metabaseuser", on_delete=models.CASCADE)  # type: ignore
    metabase_user_id = models.IntegerField(null=False, blank=False)
    metabase_group_id = models.IntegerField(null=False, blank=False, default=-1)
    metabase_db_id = models.IntegerField(null=False, blank=False, default=-1)
