from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = ('date_joined', 'avatar')


admin.site.register(CustomUser, CustomUserAdmin)
