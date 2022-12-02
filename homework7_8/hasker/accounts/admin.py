from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import Account


class AccountAdmin(UserAdmin):
    list_display = ('username', 'email', 'avatar', 'date_joined',)


admin.site.register(Account, AccountAdmin)
