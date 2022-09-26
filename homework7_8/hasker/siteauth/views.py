from django.views.generic import CreateView

from .forms import SiteUserCreateForm
from .models import SiteUser


class SiteUserCreateView(CreateView):
    model = SiteUser
    success_url = '/hasker/'
    form_class = SiteUserCreateForm
