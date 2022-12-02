from django.contrib.auth.forms import UserCreationForm, UserChangeForm


from .models import Account


class AccountCreateForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ('username', 'email', 'password1', 'password2', 'avatar')

class AccountUpdateForm(UserChangeForm):
    password =None
    class Meta:
        model = Account
        fields = ('username', 'email', 'avatar')
