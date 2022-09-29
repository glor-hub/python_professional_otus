from django.views.generic import CreateView, UpdateView
from django.contrib import messages

from .forms import SiteUserCreateForm
from .forms import SiteUserUpdateForm

from .models import SiteUser


class SiteUserCreateView(CreateView):
    model = SiteUser
    success_url = '/hasker/'
    form_class = SiteUserCreateForm

class SiteUserActionMixin:
    @property
    def success_msg(self):
        return NotImplemented

    def form_valid(self, form):
        messages.info(self.request, self.success_msg)
        return super().form_valid(form)


class SiteUserUpdateView(SiteUserActionMixin,
                         UpdateView):
    model = SiteUser
    success_url = '/hasker/'
    success_msg = "User`s data updated!"
    form_class = SiteUserUpdateForm

