from django.contrib.auth.forms import UserCreationForm

from .models import SiteUser


class SiteUserCreateForm(UserCreationForm):
    class Meta:
        model = SiteUser
        fields = ('username', 'email', 'password1', 'password2')
