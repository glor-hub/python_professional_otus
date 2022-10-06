from django.contrib import admin

from .models import Question, QuestionVote, Answer, AnswerVote, Tag


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'create_at', 'votes_total', 'rating')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    ordering = ('-votes_total', )
    list_filter = ['create_at']
    list_per_page = 5

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'body', 'question','create_at', 'votes_total', 'rating')
    ordering = ('-votes_total', )
    list_filter = ['create_at']
    list_per_page = 5

admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionVote)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswerVote)
admin.site.register(Tag)
