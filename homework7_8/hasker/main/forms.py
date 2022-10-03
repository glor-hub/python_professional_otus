from django import forms
from django.urls import reverse

from .models import Question


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'body', 'tags_string']
        label={'tags_string':'Tags'}



