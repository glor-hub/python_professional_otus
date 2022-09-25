from django.db import models
from django.utils import timezone

from users.models import CustomUser


class Tag(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title


class Question(models.Model):
    title = models.CharField(max_length=128)
    content = models.TextField()
    create_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True, related_name='questions')

    def __str__(self):
        return self.title


class QuestionVote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'question'),)


class Answer(models.Model):
    content = models.TextField()
    create_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"answer id={self.pk}: {self.content}"


class AnswerVote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'answer'),)
