from django.views.generic import CreateView, UpdateView
from django.contrib import messages

from .forms import AccountCreateForm
from .forms import AccountUpdateForm

from .models import Account


class AccountCreateView(CreateView):
    model = Account
    success_url = '/hasker/'
    form_class = AccountCreateForm

class AccountActionMixin:
    @property
    def success_msg(self):
        return NotImplemented

    def form_valid(self, form):
        messages.info(self.request, self.success_msg)
        return super().form_valid(form)


class AccountUpdateView(AccountActionMixin,
                         UpdateView):
    model = Account
    success_url = '/hasker/'
    success_msg = "User`s data updated!"
    form_class = AccountUpdateForm

