from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse

from .models import Question, Tag


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'body', 'tags_string']
        labels={'tags_string':'Tags'}
    def clean_tags_string(self):
        tags=[]
        tags_string=self.cleaned_data['tags_string']
        for tg in tags_string.split(','):
            tags.append(tg.lower())
        if len(tags) > 3:
            raise ValidationError('Сannot enter more than 3 tags')
        return tags_string

class AnswerCreateForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['body']
        labels={'body':'Your answer:'}
