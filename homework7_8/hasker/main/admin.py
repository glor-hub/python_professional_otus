from django.contrib import admin

from .models import Question, QuestionVote, Answer, AnswerVote, Tag

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title','author','create_at','votes_total')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('votes_total','tags')
    list_filter = ['create_at']

admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionVote)
admin.site.register(Answer)
admin.site.register(AnswerVote)
admin.site.register(Tag)
