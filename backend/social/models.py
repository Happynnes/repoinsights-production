from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class PrivateRepository(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # type: ignore
    owner_id = models.IntegerField()
    owner = models.CharField(max_length=255, null=True, blank=True)
    repo_id = models.IntegerField()
    repo_name = models.CharField(max_length=255)
    repo_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class UserTokens(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # type: ignore
    access_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True, blank=True, help_text="Fecha de expiración del token", default=None
    )
