from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import SiteUser


class SiteUserCreateForm(UserCreationForm):
    class Meta:
        model = SiteUser
        fields = ('username', 'email', 'password1', 'password2', 'avatar')

class SiteUserUpdateForm(UserChangeForm):
    class Meta:
        model = SiteUser
        fields = ('username', 'email', 'avatar')
