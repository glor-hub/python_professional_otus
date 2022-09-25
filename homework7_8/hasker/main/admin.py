from django.contrib import admin

from .models import Question, QuestionVote, Answer, AnswerVote, Tag

admin.site.register(Question)
admin.site.register(QuestionVote)
admin.site.register(Answer)
admin.site.register(AnswerVote)
admin.site.register(Tag)
