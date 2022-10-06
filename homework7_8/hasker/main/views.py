from time import timezone

import smtplib

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django.utils import timezone

from django.views.generic import DetailView, ListView, CreateView
from django.views.generic.edit import FormMixin

from .forms import QuestionCreateForm, AnswerCreateForm
from .models import Question, Answer, Tag
from hasker.settings import LOCALHOST, DEFAULT_FROM_EMAIL,USE_EMAIL_NOTIFICATION


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
    template_name = 'main/question_create.html'

    def form_valid(self, form):
        tag_list = []
        instance = form.save(commit=False)
        instance.author = self.request.user
        instance.save()
        tags_strings = instance.tags_string
        for tg in Tag.objects.all():
            tag_list.append(tg.title)
        for tag in tags_strings.split(','):
            if tag in tag_list:
                instance.tags.add(Tag.objects.get(title=tag))
        return super().form_valid(form)


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'main/question_detail.html'
    context_object_name = 'question'

    def get_object(self, **kwargs):
        return Question.objects.get(slug=self.kwargs['question_slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['max_ratings_list'] = Question.objects.order_by('-rating')[:2]
        return context


class QuestionView(FormMixin, QuestionDetailView):
    form_class = AnswerCreateForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.question = Question.objects.get(slug=self.kwargs['question_slug'])
        instance.save()
        flag_email=USE_EMAIL_NOTIFICATION
        if flag_email:
            recipients_email = []
            recipients_email.append(instance.question.author.email)
            link = LOCALHOST + self.get_success_url()
            send_mail(
                'Hello,',
                f'There is a new answer to your question:{link}',
                DEFAULT_FROM_EMAIL,
                recipients_email,
                fail_silently=False,
            )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('main:question_detail', kwargs={'question_slug': self.kwargs['question_slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_slug = get_object_or_404(Question, slug=self.kwargs['question_slug'])
        answers_list=Answer.objects.filter(question=question_slug)
        paginator = Paginator(answers_list, per_page=30)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)
        context['page'] = page
        context['answers_list'] = page.object_list
        return context
