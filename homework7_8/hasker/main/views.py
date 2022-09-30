from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import DetailView, ListView, CreateView

# from .forms import QuestionCreateForm
from .models import Question


# def index(request):
#     context = {
#         'title': 'Home page'
#     }
#     return render(request, 'index.html', context)


class QuestionListView(ListView):
    model = Question
    paginate_by=2

class NewQuestionListView(QuestionListView):
    template_name = 'index.html'
    ordering = ('-create_at',)


class HotQuestionListView(QuestionListView):
    template_name = 'main/question_list_hot.html'
    ordering = ('-voice_total',)


class QuestionCreateView(LoginRequiredMixin, CreateView):
    # form_class = QuestionCreateForm
    model = Question
    fields = ['title', 'body', 'tags']
    success_url = 'question/<slug:question_slug>'
    template_name = 'main/question_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        tags=form.instance.tags[:2]
        form.instance.tags=tags
        return super().form_valid(form)
