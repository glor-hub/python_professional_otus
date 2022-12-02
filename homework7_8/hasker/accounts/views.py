from django.urls import reverse
from django.views.generic import CreateView, UpdateView

from .mixins import AccountActionMixin

from .forms import AccountCreateForm
from .forms import AccountUpdateForm

from .models import Account


class AccountCreateView(CreateView):
    model = Account
    form_class = AccountCreateForm

    def get_success_url(self):
        return reverse('main:index')



class AccountUpdateView(AccountActionMixin,
                         UpdateView):
    model = Account
    success_msg = "User`s data updated!"
    form_class = AccountUpdateForm

    def get_success_url(self):
        return reverse('main:index')
