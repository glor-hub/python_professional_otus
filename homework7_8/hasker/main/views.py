from time import timezone

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.paginator import Paginator

from django.shortcuts import get_object_or_404
from django.urls import reverse

from django.utils import timezone

from django.views.generic import DetailView, ListView, CreateView
from django.views.generic.edit import FormMixin

from .forms import QuestionCreateForm, AnswerCreateForm
from .models import Question, Answer, Tag, AnswerVote, QuestionVote
from hasker.settings import LOCALHOST, DEFAULT_FROM_EMAIL, USE_EMAIL_NOTIFICATION


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


# def get_object_or_create(AnswerVote, user, answer):
#     pass


class QuestionView(FormMixin, QuestionDetailView):
    form_class = AnswerCreateForm

    def post(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            raise ValidationError(
                'To answer to question it is necessary to register.')
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
        if not Answer.objects.filter(question=instance.question, user=instance.user):
            instance.save()
        else:
            raise ValidationError("You've already answered  on this question")
        flag_email = USE_EMAIL_NOTIFICATION
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
        question = get_object_or_404(Question, slug=self.kwargs['question_slug'])
        answers_list = Answer.objects.filter(question=question).order_by('-rating', '-create_at')
        paginator = Paginator(answers_list, per_page=30)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)
        context['page'] = page
        context['answers_list'] = page.object_list
        a_dislike = self.request.GET.get('a_dislike')
        a_like = self.request.GET.get('a_like')
        if a_dislike or a_like:
            if self.request.user.is_anonymous:
                raise ValidationError(
                    'To vote it is necessary to register.')
            answer = get_object_or_404(Answer, pk=self.request.GET.get('a_pk'))
            if answer.user == self.request.user:
                raise ValidationError(
                    'You cannot vote for your own answer.')
            else:
                answer_vote, created = AnswerVote.objects.get_or_create(user=self.request.user, answer=answer)
                if a_dislike:
                    answer_vote.event_dislike = True
                if a_like:
                    answer_vote.event_like = True
                answer_vote.save()
                if answer_vote.add_like:
                    answer.votes_like += 1
                    answer_vote.add_like = False
                if answer_vote.add_dislike:
                    answer.votes_dislike += 1
                    answer_vote.add_dislike = False
                answer.save()
                answer_vote.save()
        q_dislike = self.request.GET.get('q_dislike')
        q_like = self.request.GET.get('q_like')
        if q_dislike or q_like:
            if self.request.user.is_anonymous:
                raise ValidationError(
                    'To vote it is necessary to register.')
            if question.author == self.request.user:
                raise ValidationError(
                    'You cannot vote for your own answer.')
            else:
                question_vote, created = QuestionVote.objects.get_or_create(user=self.request.user, question=question)
                if q_dislike:
                    question_vote.event_dislike = True
                if q_like:
                    question_vote.event_like = True
                question_vote.save()
                if question_vote.add_like:
                    question.votes_like += 1
                    question_vote.add_like = False
                if question_vote.add_dislike:
                    question.votes_dislike += 1
                    question_vote.add_dislike = False
                question.save()
                question_vote.save()
        return context

    # def get_vote(self,class_vote, query_obj):
    #     instanse_vote = get_object_or_404(class_vote, user=self.request.user, question=question_slug)

    # def vote_result(self, instance):
    #     a_dislike = self.request.GET.get('a_dislike')
    #     a_like = self.request.GET.get('a_like')
    #     if a_dislike:
    #         instance.event_dislike = True
    #     if a_like:
    #         instance.event_like = True
    #     instance.save()
