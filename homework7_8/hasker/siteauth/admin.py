from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from siteauth.models import SiteUser


class SiteUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'avatar', 'date_joined',)


admin.site.register(SiteUser, SiteUserAdmin)
