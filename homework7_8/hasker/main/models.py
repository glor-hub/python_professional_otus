from django.db import models
from django.utils import timezone

from users.models import CustomUser

LIKE = 'L'
DISLIKE = 'D'
NONE = 'N'
STATUS = [
    (LIKE, 'Like'),
    (DISLIKE, 'Dislike'),
    (NONE, 'None')
]


class Tag(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title


class Question(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(max_length=256)
    body = models.TextField()
    create_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    votes_total = models.IntegerField(default=0)
    votes_like = models.PositiveIntegerField(default=0)
    votes_dislike = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True, related_name='questions')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.votes_total = self.votes_like - self.votes_dislike
        super().save(*args, **kwargs)


class QuestionVote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS, default='N')
    add_like = models.BooleanField(default=False)
    add_dislike = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'question'),)

    def save(self, *args, **kwargs):
        sts = self.status
        if self.add_like:
            if sts == NONE or sts == DISLIKE:
                self.status = LIKE
            self.add_like = False
        if self.add_dislike:
            if sts == NONE or sts == LIKE:
                self.status = DISLIKE
            self.add_dislike = False
        super().save(*args, **kwargs)


class Answer(models.Model):
    body = models.TextField()
    create_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"answer id={self.pk}: {self.content}"


class AnswerVote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS, default='N')
    add_like = models.BooleanField(default=False)
    add_dislike = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'answer'),)

    def save(self, *args, **kwargs):
        sts = self.status
        if self.add_like:
            if sts == NONE or sts == DISLIKE:
                self.status = LIKE
            self.add_like = False
        if self.add_dislike:
            if sts == NONE or sts == LIKE:
                self.status = DISLIKE
            self.add_dislike = False
        super().save(*args, **kwargs)
