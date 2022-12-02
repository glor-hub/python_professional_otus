from django.views.generic import CreateView, UpdateView

from .mixins import AccountActionMixin

from .forms import AccountCreateForm
from .forms import AccountUpdateForm

from .models import Account


class AccountCreateView(CreateView):
    model = Account
    success_url = '/hasker/'
    form_class = AccountCreateForm



class AccountUpdateView(AccountActionMixin,
                         UpdateView):
    model = Account
    success_url = '/hasker/'
    success_msg = "User`s data updated!"
    form_class = AccountUpdateForm

