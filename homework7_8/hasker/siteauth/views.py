from django.views.generic import CreateView, UpdateView

from .forms import SiteUserCreateForm
from .forms import SiteUserUpdateForm
from .models import SiteUser


class SiteUserCreateView(CreateView):
    model = SiteUser
    success_url = '/hasker/'
    form_class = SiteUserCreateForm

class SiteUserUpdateView(UpdateView):
    model = SiteUser
    success_url = '/hasker/'
    form_class = SiteUserUpdateForm
