from time import timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from django.views.generic import DetailView, ListView, CreateView

from .forms import QuestionCreateForm
from .models import Question, Answer, Tag


class QuestionListView(ListView):
    model = Question
    paginate_by = 20
    context_object_name = 'object_list'

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
    form_class = QuestionCreateForm
    model = Question
    # success_url =reverse_lazy('/question/<slug:question_slug>')
    template_name = 'main/question_create.html'

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.author = self.request.user
        instance.save()
        tags_list = Tag.objects.all()
        tags_strings=instance.tags_string
        print('tags_strings',tags_strings)
        for tg in tags_strings.split(','):
            if tg.lower() in tags_list.tags:
                print(tg)
                instance.tags=tg
                print('ok')
                instance.save()
        return super().form_valid(form)


# class AnswerCreateView(LoginRequiredMixin, CreateView):
#     model = Answer
#     fields = ['body']
#     success_url = 'index.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['success_msg'] = 'Your answer added successfully'
#         return context

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'main/question_detail.html'

    def get_object(self, **kwargs):
        return Question.objects.get(slug=self.kwargs['question_slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['max_ratings_list'] = Question.objects.order_by('-rating')[:2]
        return context
