from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import DetailView, ListView, CreateView

from .forms import QuestionCreateForm
from .models import Question


def index(request):
    context = {
        'title': 'Home page'
    }
    return render(request, 'index.html', context)


class QuestionListVew(ListView):
    model = Question


class NewQuestionListVew(QuestionListVew):
    pass


class HotQuestionListVew(QuestionListVew):
    pass


class QuestionCreateView(LoginRequiredMixin,CreateView):
    form_class = QuestionCreateForm
    success_url = 'question/detail/<slug:question_slug>'
    template_name = 'main/question_create.html'
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)