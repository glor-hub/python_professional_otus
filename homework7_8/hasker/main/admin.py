from django.contrib import admin

from .models import Question, QuestionVote, Answer, AnswerVote, Tag


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'create_at', 'votes_total', 'rating')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    ordering = ('-votes_total',)
    list_filter = ['create_at']
    list_per_page = 5


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'body', 'question', 'is_favorite', 'create_at', 'votes_total', 'rating')
    ordering = ('-votes_total',)
    list_filter = ['create_at']
    list_per_page = 5


class QuestionVoteAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'status', 'add_like', 'add_dislike')
    ordering = ('question',)
    list_filter = ['user']
    list_per_page = 5


class AnswerVoteAdmin(admin.ModelAdmin):
    list_display = ('answer', 'user', 'status', 'add_like', 'add_dislike')
    ordering = ('answer',)
    list_filter = ['user']
    list_per_page = 5


admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionVote, QuestionVoteAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswerVote, AnswerVoteAdmin)
admin.site.register(Tag)
