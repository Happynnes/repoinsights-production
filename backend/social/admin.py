from django.contrib import admin
from .models import PrivateRepository, UserTokens

admin.site.register(PrivateRepository)
admin.site.register(UserTokens)
