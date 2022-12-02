from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import Account

from .constans import LIKE, DISLIKE, NONE

STATUS = [
    (LIKE, 'Like'),
    (DISLIKE, 'Dislike'),
    (NONE, 'None')
]

class Tag(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title


class Answer(models.Model):
    body = models.TextField(unique=True)
    create_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    votes_total = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)
    votes_like = models.PositiveIntegerField(default=0)
    votes_dislike = models.PositiveIntegerField(default=0)
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return f"answer id={self.pk}: {self.body}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.votes_total = self.votes_like - self.votes_dislike
        if self.votes_total < 0:
            self.votes_total = 0
        sum_votes = self.votes_like + self.votes_dislike
        if sum_votes:
            self.rating = self.votes_like * 100 / sum_votes
        else:
            self.rating = 0
        super().save(*args, **kwargs)


class Question(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(max_length=256, null=False, unique=True)
    body = models.TextField()
    create_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    votes_total = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)
    votes_like = models.PositiveIntegerField(default=0)
    votes_dislike = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name='tags')
    tags_string = models.CharField(max_length=128)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.votes_total = self.votes_like - self.votes_dislike
        if self.votes_total < 0:
            self.votes_total = 0
        sum_votes = self.votes_like + self.votes_dislike
        if sum_votes:
            self.rating = self.votes_like * 100 / sum_votes
        else:
            self.rating = 0
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('main:question_detail', kwargs={'question_slug': self.slug})

    def get_answers_count(self):
        return Answer.objects.filter(question=self).count()


class QuestionVote(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS, default='N')
    event_dislike = models.BooleanField(default=False)
    event_like = models.BooleanField(default=False)
    add_dislike = models.BooleanField(default=False)
    add_like = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'question'),)

    def save(self, *args, **kwargs):
        sts = self.status
        if self.event_like:
            if sts == NONE or sts == DISLIKE:
                self.status = LIKE
                self.add_like = True
            self.event_like = False
        if self.event_dislike:
            if sts == NONE or sts == LIKE:
                self.status = DISLIKE
                self.add_dislike = True
            self.event_dislike = False
        super().save(*args, **kwargs)


class AnswerVote(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS, default='N')
    event_dislike = models.BooleanField(default=False)
    event_like = models.BooleanField(default=False)
    add_dislike = models.BooleanField(default=False)
    add_like = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'answer'),)

    def save(self, *args, **kwargs):
        sts = self.status
        if self.event_like:
            if sts == NONE or sts == DISLIKE:
                self.status = LIKE
                self.add_like = True
            self.event_like = False
        if self.event_dislike:
            if sts == NONE or sts == LIKE:
                self.status = DISLIKE
                self.add_dislike = True
            self.event_dislike = False
        super().save(*args, **kwargs)
