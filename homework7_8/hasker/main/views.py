from time import timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils import timezone

from django.views.generic import DetailView, ListView, CreateView

# from .forms import QuestionCreateForm
from .models import Question, Answer


class QuestionListView(ListView):
    model = Question
    paginate_by = 2
    context_object_name ='object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = timezone.now
        context['max_ratings_list'] = Question.objects.order_by('-rating')[:2]
        return context


class NewQuestionListView(QuestionListView):
    template_name = 'index.html'
    ordering = ('-create_at',)


class HotQuestionListView(QuestionListView):
    template_name = 'main/question_list_hot.html'
    ordering = ('-votes_total',)



class QuestionCreateView(LoginRequiredMixin, CreateView):
    # form_class = QuestionCreateForm
    model = Question
    fields = ['title', 'body', 'tags']
    success_url = 'question/<slug:question_slug>'
    template_name = 'main/question_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.save()
        tag1,tag2 = form.instance.tags
        form.instance.tags.add(tag1,tag2)
        return super().form_valid(form)

class AnswerCreateView(LoginRequiredMixin, CreateView):
    model = Answer
    fields = ['body']
    success_url = 'index.html>'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success_msg'] = 'Your answer added successfully'
        return context