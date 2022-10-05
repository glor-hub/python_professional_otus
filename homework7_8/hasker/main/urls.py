from django.urls import path

from .views import QuestionCreateView, NewQuestionListView, HotQuestionListView, QuestionDetailView, QuestionView

app_name = 'main'

urlpatterns = [
    path('', NewQuestionListView.as_view(), name='index'),
    path('question/hot', HotQuestionListView.as_view(), name='question_list_hot'),
    path('ask/', QuestionCreateView.as_view(), name='question_create'),
    path('question/<slug:question_slug>', QuestionView.as_view(), name='question_detail'),

    # # path('search/', main.index, name='search'),
    # # path('tag/<slug:tag_slug>', main.index, name='tag'),
]
